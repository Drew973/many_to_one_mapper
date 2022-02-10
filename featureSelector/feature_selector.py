from qgis.core import QgsFeatureRequest
from qgis.utils import iface

from PyQt5.QtCore import pyqtSignal,QStringListModel

from qgis.PyQt.QtWidgets import QWidget,QCompleter


from . feature_mapper import featureMapper


'''
class for selecting features of qgis layer by value
inherits from featureMapper
inherits from QWidget because want to emit signal

'''


class featureSelector(QWidget,featureMapper):

    valueChanged = pyqtSignal(str,name='valueChanged')
    featureChanged = pyqtSignal(int,name='featureChanged')#fid of new feature
   


#needs layerBox and Fieldbox
    def __init__(self,layerBox,fieldBox,valueEdit=None,fromLayerButton=None,goToButton=None,prefix=''):
        super(featureSelector,self).__init__(layerBox=layerBox,fieldBox=fieldBox,prefix=prefix)#super calls __init__ of all parent classes

        self.layerBox=layerBox
        self.fieldBox=fieldBox
        self.fromLayerButton=fromLayerButton
        self.goToButton=goToButton
        self.valueEdit = valueEdit

        self.prefix=prefix
        
        self.initFromLayerButton()
        self.initValueEdit()
        self.initGoToButton()
        
        self.value=None
        self.feature=None

        
    def initFromLayerButton(self):
        self.fromLayerButton.clicked.connect(self.fromLayer)



    def initValueEdit(self):
        self.fieldBox.fieldChanged.connect(self.fixValueEditCompleter)
        self.valueEdit.textEdited.connect(self.fromValue)


    def initGoToButton(self):
       # self.goToButton.clicked.connect(lambda:self.setValue(value=self.valueEdit.text(),select=True))
        self.goToButton.clicked.connect(self.fromValue)


    #set feature to selected feature of layer
    def fromLayer(self):              
        feat=self.getSelectedFeature()
        if feat:
            self.setFeature(feat)



    #set feature to feature with field=value
    def fromValue(self,value=None):
        if not value:
            value=self.valueEdit.text()
            
        feat=self.getFeature(value)#will give warnings if layer,field not set,feature does not exist or multiple features
        if feat:
            self.setFeature(feat,zoom=True,select=True)
    

    def selectOnLayer(self):
        feat=self.currentFeature()
        if feat:
            self.selectFids(feat.id())


#assume feature is in layer
    def setFeature(self,feature,zoom=False,select=False):
        self.feature=feature
        field=self.getField()
        self.featureChanged.emit(feature.id())
        
        if field:
            self.valueEdit.setText(toString(feature[field]))

        if select:
            #select this feature on layer
            self.selectFids([feature.id()])

        if zoom:
            #zoom to selected feature of layer
            self.zoomToSelected()

            

    #setup completer for valueEdit based on unique values of layer and field 
    def fixValueEditCompleter(self,field):
        layer=self.getLayer()
        if layer:
            completer = QCompleter()
            self.valueEdit.setCompleter(completer)
            completer.setModel(toStringListModel(layer,field))


    def currentValue(self):
        field=self.getField()
        if field:
            return self.currentFeature[field]


    def currentFeature(self,warnings=True):
        if self.feature:
            return self.feature
        if warnings:
            iface.messageBar().pushMessage('%s no feature selected'%(self.prefix),duration=5)



#makes unique values into QStringListModel. Works with any type of field.
def toStringListModel(layer,field):
    model=QStringListModel()
    col_index=layer.dataProvider().fieldNameIndex(field)
    #model.setStringList(layer.uniqueValues(col_index))
    model.setStringList([toString(v) for v in layer.uniqueValues(col_index)])    
    return model



#converts to string.
def toString(v):
    if isinstance(v,float):          
        if v.is_integer():
            return str(int(v))
        else:
            return str(v)
    else:
        return str(v)



