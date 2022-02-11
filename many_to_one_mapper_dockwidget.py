import os

import csv

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal,Qt,QUrl

from . many_to_one_mapper_dockwidget_base import Ui_manyToOneMapperDockWidgetBase
from qgis.utils import iface


from . import model


class ManyToOneMapperDockWidget(QtWidgets.QDockWidget, Ui_manyToOneMapperDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(ManyToOneMapperDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.prefix='Many To One Mapper: '
        
        self.menuBar = QtWidgets.QMenuBar()
        self.initFileMenu()
        self.initToolsMenu()
        self.initAccidentsMenu()
        self.initHelpMenu()

        self.mainWidget.layout().setMenuBar(self.menuBar)

        self.layerBox1.layerChanged.connect(self.fieldBox1.setLayer)
        self.fieldBox1.setLayer(self.layerBox1.currentLayer())

        self.layerBox2.layerChanged.connect(self.fieldBox2.setLayer)
        self.fieldBox2.setLayer(self.layerBox2.currentLayer())

        self.featuresBox.setField(self.fieldBox1.currentField(),self.layerBox1.currentLayer())
        self.fieldBox1.fieldChanged.connect(lambda field:self.featuresBox.setField(field,self.layerBox1.currentLayer()))
        
        self.nextButton.clicked.connect(self.featuresBox.next)
        self.lastButton.clicked.connect(self.featuresBox.last)
        
        self.fromLayerButton.clicked.connect(self.fromLayer)
        
        self.model = model.model()
    
        self.fieldBox2.fieldChanged.connect(self.changeFeature)
        self.layerBox2.layerChanged.connect(self.changeFeature)        
        self.featuresBox.currentIndexChanged.connect(self.changeFeature)
        self.changeFeature()
        

    def currentKey(self):
        return model.key(self.featuresBox.feature(),self.layerBox1.currentLayer(),self.layerBox2.currentLayer())


    def changeFeature(self):
        self.view.setModel(self.model.toStandardItemModel(self.currentKey(),self.fieldBox2.currentField()))
        if self.zoomBox.isChecked():
            self.featuresBox.selectOnLayer()
            self.selectAllOnLayer()
        

    #drops all rows for current feature
    def clear(self):
        self.model.clear(self.currentKey())

        

    def selectAllOnLayer(self):
        self.layerBox2.currentLayer().selectByIds(self.model.fids(self.currentKey()))

        
    def selectOnLayer(self):
        self.layerBox2.currentLayer().selectByIds(self.model.fids(self.currentKey(),self.selectedRows()))
    
        
    def selectedRows(self):
        return [i.row() for i in self.view.selectionModel().selectedRows()]


    def addSelectedFeatures(self):
        
        for feat in self.featuresBox.currentFeatures():
            self.model.addFeatures(self.currentKey(),self.layerBox2.currentLayer().selectedFeatures())

        self.changeFeature()


    def dropSelectedRows(self):
        self.model.removeRows(self.currentKey(),self.selectedRows())
        self.changeFeature()
    
        
    def fromLayer(self):
        result,message = self.featuresBox.fromLayer()
        if not result:
             iface.messageBar().pushMessage(message,duration=5)
        
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    def initFileMenu(self):
        self.fileMenu = QtWidgets.QMenu("File")  
        self.saveAct=self.fileMenu.addAction('Save as csv...')
        self.saveAct.triggered.connect(self.save)
        self.loadAct=self.fileMenu.addAction('Load csv...')
        self.loadAct.triggered.connect(self.load)
        self.menuBar.addMenu(self.fileMenu)


    def initToolsMenu(self):
        self.toolsMenu = QtWidgets.QMenu("Edit")  

        addSelectedAct = self.toolsMenu.addAction('Add selected features')
        addSelectedAct.triggered.connect(self.addSelectedFeatures)

        self.addWithinGeomAllAct=self.toolsMenu.addAction('add features within geometry to all')
        self.addWithinGeomAllAct.triggered.connect(self.addWithinGeomAll)

        addWithinGeomAct = self.toolsMenu.addAction('add features within geometry')
        addWithinGeomAct.triggered.connect(self.addWithinGeom)
        
        self.menuBar.addMenu(self.toolsMenu)



        clearAct = self.toolsMenu.addAction('Clear')
        clearAct.triggered.connect(self.clear)


    def initHelpMenu(self):
        self.helpMenu = QtWidgets.QMenu("Help")  
        self.openHelpAct=self.helpMenu.addAction('Open help (in your default web browser)')
        self.openHelpAct.triggered.connect(self.openHelp)
        self.menuBar.addMenu(self.helpMenu)        


    def save(self):
        to = QtWidgets.QFileDialog.getSaveFileName(caption='save as',filter='*.csv;;*')[0]
        if to:
            self.model.writeCSV(to,self.layerBox1.currentLayer(),self.fieldBox1.currentField(),self.layerBox2.currentLayer(),self.fieldBox2.currentField())


    def load(self):
        f = QtWidgets.QFileDialog.getOpenFileName(caption='load',filter='*.csv;;*')[0]
        if f:
            self.model.readCSV(f,self.layerBox1.currentLayer(),self.fieldBox1.currentField(),self.layerBox2.currentLayer(),self.fieldBox2.currentField())
            self.changeFeature()

    
#for requested view
    def initAccidentsMenu(self):
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
        self.model.addWithinGeom(self.featuresBox.feature(),self.layerBox1.currentLayer(),self.layerBox2.currentLayer())
        self.changeFeature()    


#addWithinGeom for all sections
    def addWithinGeomAll(self):
        self.model.addWithinGeomAll(self.layerBox1.currentLayer(),self.layerBox2.currentLayer())        
        self.changeFeature()
    

#primary is feature of primary layer.
#secondary is feature of secondary layer


