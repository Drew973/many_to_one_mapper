
#makes list from unique values of layer.field
#can find or select features matching current value.
if __name__=='__console__':
    import sys
    p = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\manytoonemapper\featuresWidget'
    sys.path.append(p)
    
    
from . import searchableComboBox



from qgis.core import QgsFeatureRequest
from qgis.utils import iface
#from PyQt5.QtCore import pyqtSignal




'''
widget to map layer and field to features. For 1:1 mapping use a unique field 
'''




class featuresWidget(searchableComboBox.searchableComboBox):
#
  #  featuresChanged = pyqtSignal()
    
    def __init__(self,parent=None):
        super().__init__(parent)
     
        self.layer = None
        self.field = None
    
    
    #string,QgsVectorLayer
       
    def setField(self,field,layer):
        self.layer = layer
        self.field = field
        self.clear()
        if not self.layer is None:
            self.addItems([str(v) for v in self.layer.uniqueValues(self.layer.fields().indexOf(field))])
    
    
    def next(self):
        #count starts from 1. index starts from 0
        if self.currentIndex()<self.count()-1:
            self.setCurrentIndex(self.currentIndex()+1)
        
        
    def last(self):
        if self.currentIndex()>0:
            self.setCurrentIndex(self.currentIndex()-1)


    def currentFeatures(self):        
        if self.layer and self.field:
            e = '%s=%s '%(double_quote(self.field),single_quote(self.currentValue()))
            request = QgsFeatureRequest().setFilterExpression(e)
            return [f for f in self.layer.getFeatures(request)]
        return []


    def fromLayer(self):
        vals = [str(f[self.field]) for f in self.layer.selectedFeatures()]
        
        vals = list(set(vals)) #unique values
        
        if len(vals)==0:
            return False,'no features selected'
        
        if len(vals)>1:
            return False,'>1 value in selected features'
        
        if len(vals)==1:
            self.setCurrentIndex(self.findText(vals[0]))
            return True,'no error'
        
        
        
    def selectOnLayer(self):
        self.layer.selectByIds([f.id() for f in self.currentFeatures()])
        zoomToSelected(self.layer)
        
        
def single_quote(s):
    return "'%s'"%(s)


def double_quote(s):
    return '"%s"'%(s)         

        
def zoomToSelected(layer):
    a = iface.activeLayer()
    iface.setActiveLayer(layer)
    iface.actionZoomToSelected().trigger()
    iface.setActiveLayer(a)
    




class featureWidget(featuresWidget):

    def feature(self):
        f = self.currentFeatures()
        if len(f)==1:
            return f[0]

            
    
            
if __name__=='__console__':
    from PyQt5.QtWidgets import QWidget,QHBoxLayout,QPushButton

    w = QWidget()
    w.setLayout(QHBoxLayout())
    
    f = featuresWidget()
    w.layout().addWidget(f)
    
    nextButton = QPushButton('next')
    nextButton.clicked.connect(f.next)
    
    w.layout().addWidget(nextButton)
    


    w.show()

    layer = QgsProject.instance().mapLayersByName('buffers')[0]
    f.setLayer(layer)
    f.setField('segment_no')
    f.setField('seg_no_int')