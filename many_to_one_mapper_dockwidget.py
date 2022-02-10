import os

import csv

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal,Qt,QUrl

from .featureSelector.feature_selector import featureSelector
from .featureSelector.feature_mapper import featureMapper


from . many_to_one_mapper_dockwidget_base import Ui_manyToOneMApperDockWidgetBase
from qgis.utils import iface

import ast


#uiPath=os.path.join(os.path.dirname(__file__), 'many_to_one_mapper_dockwidget_base.ui')
#FORM_CLASS, _ = uic.loadUiType(uiPath)



class ManyToOneMapperDockWidget(QtWidgets.QDockWidget, Ui_manyToOneMApperDockWidgetBase):

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

        self.fieldBox1.setLayer(self.layerBox1.currentLayer())
        self.layerBox1.layerChanged.connect(self.fieldBox1.setLayer)        
       
        
        self.layerBox2.layerChanged.connect(self.fieldBox2.setLayer)
        self.fieldBox2.setLayer(self.layerBox2.currentLayer())

        self.featureSelector = featureSelector(layerBox=self.layerBox1,fieldBox=self.fieldBox1,valueEdit=self.valueEdit,fromLayerButton=self.fromLayerButton,goToButton=self.goToButton,prefix=self.prefix+'layer')
    
        self.model=  {}#uses fids
        self.tableModel=QtGui.QStandardItemModel(self)
        self.view.setModel(self.tableModel)

        self.featureSelector.valueChanged.connect(self.changeVal)
        self.featureSelector.featureChanged.connect(lambda fid:self.changeFeature(self.featureSelector.fidToFeat(fid)))

        self.accidentMapper = featureMapper(self.layerBox2,self.fieldBox2,self.prefix+'join')

        self.fieldBox2.fieldChanged.connect(lambda:self.changeFeature())

        self.layerBox1.layerChanged.connect(self.featuresBox.setLayer)
        self.featuresBox.setLayer(self.layerBox1.currentLayer())
        
        self.fieldBox1.fieldChanged.connect(self.featuresBox.setField)
        self.featuresBox.setField(self.fieldBox1.currentField())
        
        self.nextButton.clicked.connect(self.featuresBox.next)
        self.lastButton.clicked.connect(self.featuresBox.last)
        
        self.fromLayerButton.clicked.connect(self.fromLayer)
        self.goToButton.clicked.connect(self.featuresBox.selectOnLayer)
        
        
        
        
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
        self.toolsMenu = QtWidgets.QMenu("Tools")  
        self.addWithinGeomAllAct=self.toolsMenu.addAction('add features within geometry to all')
        self.addWithinGeomAllAct.triggered.connect(self.addWithinGeomAll)
        self.menuBar.addMenu(self.toolsMenu)


    def initHelpMenu(self):
        self.helpMenu = QtWidgets.QMenu("Help")  
        self.openHelpAct=self.helpMenu.addAction('Open help (in your default web browser)')
        self.openHelpAct.triggered.connect(self.openHelp)
        self.menuBar.addMenu(self.helpMenu)        


#for requested view
    def initAccidentsMenu(self):
        self.accidentsMenu = QtWidgets.QMenu()
        
        addSelectedact=self.accidentsMenu.addAction('Add selected features')
        addSelectedact.triggered.connect(self.addSelectedValues)

        dropSelectedrowsAct=self.accidentsMenu.addAction('Drop selected rows.')
        dropSelectedrowsAct.triggered.connect(self.dropSelectedRows)

        selectOnLayerAct=self.accidentsMenu.addAction('Select on layer')
        selectOnLayerAct.triggered.connect(self.selectOnLayer)

        addWithinGeomAct=self.accidentsMenu.addAction('add features within geometry')
        addWithinGeomAct.triggered.connect(self.addWithinGeom)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.view.customContextMenuRequested.connect(lambda pt:self.accidentsMenu.exec_(self.view.mapToGlobal(pt)))

        
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()



#opens help/index.html in default browser
    def openHelp(self):
        helpPath = os.path.join(os.path.dirname(__file__),'help','overview.html')
        helpPath = 'file:///'+os.path.abspath(helpPath)
        print(helpPath)
        QtGui.QDesktopServices.openUrl(QUrl(helpPath))
        


                
#checks all values in fields are unique
#only need values in model to be unique

    def save(self):
        primaryField=self.featureSelector.getField()
        secondaryField=self.accidentMapper.getField()


        if primaryField and secondaryField:
            if self.featureSelector.fieldHasDuplicateValues():
                iface.messageBar().pushMessage('%s %s has duplicate values'%(self.prefix,primaryField))       
                return

            
            if self.accidentMapper.fieldHasDuplicateValues():
                iface.messageBar().pushMessage('%s %s has duplicate values'%(self.prefix,secondaryField))       
                return
            
            self.saveGrouped(primaryFields=[primaryField],secondaryFields=[secondaryField])



    def saveGrouped(self,includePrimaryId=False,includeSecondaryId=False,includeCount=True,primaryFields=[],secondaryFields=[]):
        to = QtWidgets.QFileDialog.getSaveFileName(caption='save as',filter='*.csv;;*')[0]
        if to:
            columns=[]
            
            if includePrimaryId:
                columns.append('primaryId')

            columns += primaryFields

            if includeSecondaryId:
                columns.append('secondaryId')

            columns += secondaryFields
            
            if includeCount:
                columns.append('count')

            
            with open(to,'w',newline='') as f:
                writer=csv.DictWriter(f,columns)
                writer.writeheader()
        
                for k in self.model.keys():
                    vals=self.featureSelector.fidToValuesDict(k,primaryFields)
                    vals.update(self.accidentMapper.fidsToValues(self.model[k],secondaryFields))

                    if includePrimaryId:
                        vals.update({'primaryId':k})
            
                    if includeSecondaryId:
                        vals.update({'secondaryId':self.model[k]})
                    
                    if includeCount:
                        vals.update({'count':len(self.model[k])})
                        
                    writer.writerow(vals)

                iface.messageBar().pushMessage(self.prefix+'saved as %s'%(to))       



    def load(self):
        toLoad = QtWidgets.QFileDialog.getOpenFileName(caption='load csv',filter='*.csv;;*')#(file,filter)
        if toLoad:
            toLoad=toLoad[0]#lose filter
            primaryField=self.featureSelector.getField()
            secondaryField=self.accidentMapper.getField()

            hasErrors=False

            if primaryField and secondaryField:
                
                self.model={}
                            
                with open(toLoad,'r') as f:
                    reader=csv.DictReader(f)

                    if not primaryField in reader.fieldnames:
                        iface.messageBar().pushMessage(self.prefix+'error loading %s: csv has no field named %s'%(toLoad,primaryField))       
                        return


                    if not secondaryField in reader.fieldnames:
                        iface.messageBar().pushMessage(self.prefix+'error loading %s: csv has no field named %s'%(toLoad,secondaryField))       
                        return
                    
                    
                    for row in reader:#row is dict produced by csv.reader
                        if not self.loadRow(row,primaryField,secondaryField):
                            hasErrors=True

                        
                    if hasErrors:
                        iface.messageBar().pushMessage(self.prefix+'loaded %s. csv has bad lines'%(toLoad))
                    else:
                        iface.messageBar().pushMessage(self.prefix+'loaded %s.'%(toLoad))
                    
                    self.changeFeature()


        
#row is dict produced by csv.reader
#loads row and returns True if no problems
                    
    def loadRow(self,row,primaryField,secondaryField):
        primaryFeat=self.featureSelector.getFeature(row[primaryField])
        secondaryFeats = [self.accidentMapper.getFeature(v) for v in ast.literal_eval(row[secondaryField])]#literal_eval converts string to list


        if not primaryFeat:
            return False
        
        if None in secondaryFeats:
            return False
            
        self.addFeatures(secondaries=[f for f in secondaryFeats if f],primary=primaryFeat)#none null features
        return True

        


    def addSelectedValues(self):
        self.addFeatures(self.accidentMapper.getSelectedFeatures(),self.featureSelector.currentFeature())
        
    
    def selectOnLayer(self):
        self.accidentMapper.selectFids(self.selectedFids())
        self.accidentMapper.zoomToSelected()


    def selectedFids(self):
        return [i.sibling(i.row(),0).data() for i in self.view.selectionModel().selectedRows()]

    

    def dropSelectedRows(self):
        fid=self.featureSelector.currentFeature().id()
        for f in self.selectedFids():
            self.model[fid].remove(f)
        self.changeFeature(self.featureSelector.currentFeature())


#primary is feature of primary layer.
#secondary is feature of secondary layer


#model is dict of primary fid:[secondary fids]     
    def addFeatures(self,secondaries,primary):
    
        if not primary:
            iface.messageBar().pushMessage(self.prefix+'no feature')      
            return
            
        if secondaries:

            if primary.id() in self.model:
                self.model[primary.id()]+=[s.id() for s in secondaries if not s.id() in self.model[primary.id()]]

            else:
                self.model.update({primary.id():[s.id() for s in secondaries]})


            if primary==self.featureSelector.currentFeature(warnings=False):
                self.changeFeature(self.featureSelector.currentFeature())#refresh list



#add all accidents within or intersecting geometry of section
#feat is feature for section
    def addWithinGeom(self,feat=None):
        if not feat:
            feat=self.featureSelector.currentFeature()

        if feat:
            buffer = feat.geometry()
            self.addFeatures(secondaries=[f for f in self.accidentMapper.getAllFeatures() if buffer.contains(f.geometry())],primary=feat)

        



#addWithinGeom for all sections
    def addWithinGeomAll(self):

        for f in self.featureSelector.getAllFeatures():
            self.addWithinGeom(f)
            iface.messageBar().pushMessage(self.prefix+'added features of join layer within geometry to all')       

        self.changeFeature()


#display list for this feature
            
    def changeFeature(self,feature=None,noFeatureWarning=False):
        if not feature:
            feature=self.featureSelector.currentFeature(noFeatureWarning)

        self.tableModel.clear()

        if feature:
            
            if feature.id() in self.model:
                if self.accidentMapper.fieldIsSet():
                    field=self.accidentMapper.getField()
                    self.tableModel.setHorizontalHeaderLabels(['id',field])
                    
                    for fid in self.model[feature.id()]:
                        self.tableModel.appendRow([makeItem(fid),makeItem(self.accidentMapper.fidToValue(fid))])

                else:
                    self.tableModel.setHorizontalHeaderLabels(['id'])
                    for fid in self.model[feature.id()]:
                        self.tableModel.appendRow([makeItem(fid)])
                    


def makeItem(data):
    item=QtGui.QStandardItem()
    item.setData(data,role=Qt.EditRole )
    return item
