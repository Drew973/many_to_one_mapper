import os

import csv

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal,Qt,QUrl

from . many_to_one_mapper_dockwidget_base import Ui_manyToOneMapperDockWidgetBase
from qgis.utils import iface

from qgis.core import QgsRectangle
from . import selection_dialog

from . import model,layerFunctions,settings_dialog



class ManyToOneMapperDockWidget(QtWidgets.QDockWidget, Ui_manyToOneMapperDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(ManyToOneMapperDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.layersDialog = settings_dialog.settingsDialog(self)
        self.colorsDialog = selection_dialog.selectionDialog(self)
        
        self.prefix='Many To One Mapper: '
        
        self.initTopMenu()
        self.initTableMenu()


        self.featuresBox.setField(self.field1(),self.layer1())
        self.layersDialog.field1.fieldChanged.connect(lambda field:self.featuresBox.setField(field,self.layer1()))
        self.layersDialog.layer1.layerChanged.connect(lambda layer:self.featuresBox.setField(self.field1(),layer))#field changed not always emited by setLayer()

        self.nextButton.clicked.connect(self.featuresBox.next)
        self.lastButton.clicked.connect(self.featuresBox.last)
        
        self.fromLayerButton.clicked.connect(self.fromLayer)
        
        self.model = model.model()
    
        self.layersDialog.field2.fieldChanged.connect(self.changeFeature)
        self.layersDialog.layer2.layerChanged.connect(self.changeFeature)        
        self.featuresBox.currentIndexChanged.connect(self.changeFeature)
        self.changeFeature()

        
#saves some typing and make it easy to rename these
    def layer1(self):
        return self.layersDialog.layer1.currentLayer()

    def layer2(self):
        return self.layersDialog.layer2.currentLayer()

    def field1(self):
        return self.layersDialog.field1.currentField()

    def field2(self):
        return self.layersDialog.field2.currentField()

    def layer3(self):
        return self.layersDialog.layer3.currentLayer()


    def field3(self):
        return self.layersDialog.field3.currentField()
        

    

#filters on layer can cause this to be None
    def currentKey(self):
        #return model.key(self.featuresBox.feature(),self.layer1(),self.layer2())
        return model.key(self.featuresBox.currentFid(),self.layer1(),self.layer2())


    '''index argument to avoid connected currentIndexChanged passing zoom
        filter layer to feature 
       select feature if checkbox ticked and layer set and field set.      
       currentValue of featureWidget can be null
    '''
    def changeFeature(self,index = None,zoom=None):
        
        if zoom is None:
            zoom = self.zoomBox.isChecked()

        extent = QgsRectangle()
        
        def handleLayer(layer,e,filt,select):
                
            if e and not layer is None:
                if filt:
                    layer.setSubsetString(e)

                if select:
                    layer.selectByExpression(e)

                for f in layer.getFeatures(e):
                    extent.combineExtentWith(f.geometry().boundingBox())


        def filterExpression(layer,field):
            v = self.featuresBox.currentValue()
            if v:
                return layerFunctions.filterString(layer.fields(),field,v)
            else:
                return '1=2'

        layer1 = self.layer1()
        field1 = self.field1()
        
        if layer1 and field1:
            e = filterExpression(layer1,field1)
            handleLayer(layer1,e,self.layersDialog.filter1.isChecked(),self.layersDialog.select1.isChecked())
        
        
        layer2 = self.layer2()
        field2 = self.field2()                
        
        
        if field2:
            self.view.setModel(self.model.toStandardItemModel(self.currentKey(),self.field2()))
            if layer2:
                vals = self.model.atts(self.currentKey(),field2)
                if vals:
                    e = layerFunctions.fieldInVals(layer2.fields(),field2,vals)
                else:
                    e = '1=2' #filter out everything
                
                handleLayer(layer2,e,self.layersDialog.filter2.isChecked(),self.layersDialog.select2.isChecked())
            
        
        layer3 = self.layer3()
        field3 = self.field3()
        
        if layer3 and field3:
            e = filterExpression(layer3,field3)
            handleLayer(layer3,e,self.layersDialog.filter3.isChecked(),self.layersDialog.select3.isChecked())


        if zoom:
            extent.scale(1.1)#increase size by factor so selected features not on edge of screen
            iface.mapCanvas().setExtent(extent)
            iface.mapCanvas().refresh()
        
#layer1.selectByIds([self.featuresBox.currentFid()])    
#layer1.getGeometry(self.featuresBox.currentFid())


    #drops all rows for current feature
    def clear(self):
        self.model.clear(self.currentKey())
        self.changeFeature()
        
    
        
    def selectedRows(self):
        return [i.row() for i in self.view.selectionModel().selectedRows()]


    def addSelectedFeatures(self):
        
        for feat in self.featuresBox.currentFeatures():
            self.model.addFeatures(self.currentKey(),self.layer2().selectedFeatures())

        self.changeFeature(zoom=False)


    def dropSelectedRows(self):
        self.model.removeRows(self.currentKey(),self.selectedRows())
        self.changeFeature(zoom=False)
    
        
    def fromLayer(self):
        result,message = self.featuresBox.fromLayer()
        if not result:
             iface.messageBar().pushMessage(message,duration=5)
        
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    def initTopMenu(self):
        self.menuBar = QtWidgets.QMenuBar()
        
        #file menu
        self.fileMenu = QtWidgets.QMenu("File")  
        self.saveAct=self.fileMenu.addAction('Save as csv...')
        self.saveAct.triggered.connect(self.save)
        self.loadAct=self.fileMenu.addAction('Load csv...')
        self.loadAct.triggered.connect(self.load)
        self.menuBar.addMenu(self.fileMenu)


        #tools menu
        self.editMenu = QtWidgets.QMenu("Edit")  

        addSelectedAct = self.editMenu.addAction('Add selected features')
        addSelectedAct.triggered.connect(self.addSelectedFeatures)

        self.addWithinGeomAllAct = self.editMenu.addAction('Add features within geometry to all...')
        self.addWithinGeomAllAct.triggered.connect(self.addWithinGeomAll)

        addWithinGeomAct = self.editMenu.addAction('Add features within geometry')
        addWithinGeomAct.setToolTip('Adds all features of layer 2 contained within layer 3 geometry')
        addWithinGeomAct.triggered.connect(self.addWithinGeom)
        
        clearAct = self.editMenu.addAction('Clear')
        clearAct.setToolTip('Remove all rows for current feature')
        clearAct.triggered.connect(self.clear)
           
        self.editMenu.setToolTipsVisible(True)
        self.menuBar.addMenu(self.editMenu)


        #layers menu
        self.layersMenu = QtWidgets.QMenu("Settings")
        setLayersAct = self.layersMenu.addAction('Layers...')
        setLayersAct.triggered.connect(self.layersDialog.show)
        
        setColorAct = self.layersMenu.addAction('Set selection color...')
        setColorAct.triggered.connect(self.colorsDialog.exec)

        self.menuBar.addMenu(self.layersMenu)
        

        #help menu
        self.helpMenu = QtWidgets.QMenu("Help")  
        self.openHelpAct=self.helpMenu.addAction('Open help (in your default web browser)')
        self.openHelpAct.triggered.connect(self.openHelp)
        self.menuBar.addMenu(self.helpMenu)        


        self.mainWidget.layout().setMenuBar(self.menuBar)


    def selectOnLayer(self):
        self.layer2().selectByIds(self.model.fids(self.currentKey(),self.selectedRows()))
        

    def save(self):
        to = QtWidgets.QFileDialog.getSaveFileName(caption='save as',filter='*.csv;;*')[0]
        if to:
            self.model.writeCSV(to,self.layer1(),self.field1(),self.layer2(),self.field2())


    def load(self):
        f = QtWidgets.QFileDialog.getOpenFileName(caption='load',filter='*.csv;;*')[0]
        if f:
            self.model.readCSV(f,self.layer1(),self.field1(),self.layer2(),self.field2())
            self.changeFeature(zoom=False)

    
#for requested view
    def initTableMenu(self):
        #context menu for table
        self.accidentsMenu = QtWidgets.QMenu()
        
        dropSelectedrowsAct = self.accidentsMenu.addAction('Drop selected rows.')
        dropSelectedrowsAct.triggered.connect(self.dropSelectedRows)

        selectOnLayerAct = self.accidentsMenu.addAction('Select on layer')
        selectOnLayerAct.triggered.connect(self.selectOnLayer)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.view.customContextMenuRequested.connect(lambda pt:self.accidentsMenu.exec_(self.view.mapToGlobal(pt)))

        
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()



#opens help/index.html in default browser
    def openHelp(self):
        helpPath = os.path.join(os.path.dirname(__file__),'help','overview.html')
        helpPath = 'file:///'+os.path.abspath(helpPath)
        QtGui.QDesktopServices.openUrl(QUrl(helpPath))
        

#add all accidents within or intersecting geometry of section
#feat is feature for section
    def addWithinGeom(self):
        layer3 = self.layer3()
        field3 = self.field3()
        layer2 = self.layer2()
        
        if layer3 and field3 and layer2:
        
            e = layerFunctions.filterString(layer3.fields(),field3,self.featuresBox.currentValue())
            #geoms = [f.geometry() for f in layerFunctions.getFeatures(self.layer3(),self.field3(),self.featuresBox.currentValue())]
            geoms = [f.geometry() for f in layer3.getFeatures(e)]
            self.model.addFeatures(self.currentKey(),layerFunctions.featuresWithinGeometries(geoms,layer2))
            self.changeFeature(zoom=False)



#addWithinGeom for all sections
    def addWithinGeomAll(self):
    
        reply = QMessageBox.question(self,self.prefix, "Add within geometry for all features?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.model.addWithinGeomAll(self.layer1(),self.layer2(),self.layer3(),self.field1(),self.field3())
            self.changeFeature(zoom=False)

        

    

#primary is feature of primary layer.
#secondary is feature of secondary layer


