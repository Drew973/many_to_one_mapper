import os

import csv

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal,Qt,QUrl

from . many_to_one_mapper_dockwidget_base import Ui_manyToOneMapperDockWidgetBase
from qgis.utils import iface
from . import layers_dialog

from . import model,layerFunctions


class ManyToOneMapperDockWidget(QtWidgets.QDockWidget, Ui_manyToOneMapperDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(ManyToOneMapperDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.layersDialog = layers_dialog.layersDialog(self)
        self.prefix='Many To One Mapper: '
        
        self.initTopMenu()
        self.initTableMenu()

        #self.layerBox1.layerChanged.connect(self.fieldBox1.setLayer)
       # self.fieldBox1.setLayer(self.layerBox1.currentLayer())

       # self.layerBox2.layerChanged.connect(self.fieldBox2.setLayer)
       # self.fieldBox2.setLayer(self.layerBox2.currentLayer())


        self.featuresBox.setField(self.layersDialog.field1.currentField(),self.layer1())
        self.layersDialog.field1.fieldChanged.connect(lambda field:self.featuresBox.setField(field,self.layer1()))
        
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


    def currentKey(self):
        return model.key(self.featuresBox.feature(),self.layer1(),self.layer2())


    def changeFeature(self,zoom=None):
        if zoom is None:
            zoom = self.zoomBox.isChecked()
        
        if self.currentKey():
            self.view.setModel(self.model.toStandardItemModel(self.currentKey(),self.field2()))
            if zoom:
                self.selectOnLayer3()
                self.selectOnLayer2()
                self.featuresBox.selectOnLayer()#this should be last in case layer1=layer2 or layer3 


    def selectOnLayer3(self):
        layer = self.layer3()
        if layer:
            fids = [f.id() for f in layerFunctions.getFeatures(layer,self.field3(),self.featuresBox.currentValue())]
            layer.selectByIds(fids)
            layerFunctions.zoomToSelected(layer)


    #drops all rows for current feature
    def clear(self):
        self.model.clear(self.currentKey())
        self.changeFeature()
        

    def selectOnLayer2(self):
        self.layer2().selectByIds(self.model.fids(self.currentKey()))

        
    def selectOnLayer(self):
        self.layer2().selectByIds(self.model.fids(self.currentKey(),self.selectedRows()))
    
        
    def selectedRows(self):
        return [i.row() for i in self.view.selectionModel().selectedRows()]


    def addSelectedFeatures(self):
        
        for feat in self.featuresBox.currentFeatures():
            self.model.addFeatures(self.currentKey(),self.layer2().selectedFeatures())

        print(self.currentKey())
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
        self.toolsMenu = QtWidgets.QMenu("Edit")  

        addSelectedAct = self.toolsMenu.addAction('Add selected features')
        addSelectedAct.triggered.connect(self.addSelectedFeatures)

        self.addWithinGeomAllAct=self.toolsMenu.addAction('Add features within geometry to all')
        self.addWithinGeomAllAct.triggered.connect(self.addWithinGeomAll)

        addWithinGeomAct = self.toolsMenu.addAction('Add features within geometry')
        addWithinGeomAct.triggered.connect(self.addWithinGeom)
        
        clearAct = self.toolsMenu.addAction('Clear')
        clearAct.triggered.connect(self.clear)

        self.menuBar.addMenu(self.toolsMenu)


        #layers menu
        self.layersMenu = QtWidgets.QMenu("Layers")
        setLayersAct = self.layersMenu.addAction('Set layers')
        setLayersAct.triggered.connect(self.layersDialog.show)
        self.menuBar.addMenu(self.layersMenu)
        

        #help menu
        self.helpMenu = QtWidgets.QMenu("Help")  
        self.openHelpAct=self.helpMenu.addAction('Open help (in your default web browser)')
        self.openHelpAct.triggered.connect(self.openHelp)
        self.menuBar.addMenu(self.helpMenu)        


        self.mainWidget.layout().setMenuBar(self.menuBar)



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
        self.model.addWithinGeom(self.featuresBox.feature(),self.layer1(),self.layer2())
        self.changeFeature(zoom=False)    


#addWithinGeom for all sections
    def addWithinGeomAll(self):
        reply = QMessageBox.question(self,self.prefix, "Add within geometry for all features?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.addWithinGeomAll(self.layer1(),self.layer2())        
            self.changeFeature(zoom=False)

        

    

#primary is feature of primary layer.
#secondary is feature of secondary layer


