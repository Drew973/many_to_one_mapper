from qgis.gui import QgsFieldComboBox
from qgis.core import QgsFields

'''
QgsFieldComboBox allowing a function to be used as an additional filter.
this takes 2 arguments; field and layer. fields will be included where this returns True.

'''


class layerBox(QgsFieldComboBox):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.filterFunction = None
        self.cl = None

    
    def setLayer(self,layer):        
        super().setLayer(layer)#fieldChanged emmited here?
        
        self.cl = layer
        #remove fields if filterFunction(field,layer) is not true
        if not self.filterFunction is None:
            fields = QgsFields()
            for f in self.fields():
                if self.filterFunction(f,layer):
                    fields.append(f)
            self.setFields(fields)#'will override layer'


    def setFilterFunction(self,function):
        self.filterFunction = function


    def currentField(self):
        return self.itemText(self.currentIndex())


    def currentLayer(self):
        return self.cl

    
#QgsFieldComboBox showing only unique fields
class uniqueFieldBox(layerBox):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setFilterFunction(uniqueField)

        
def uniqueField(field,layer):
    i = layer.fields().indexFromName(field.name())    
    return not layer.featureCount() >len(layer.uniqueValues(i))

        
if __name__=='__console__':
    b = uniqueFieldBox()
    layer = QgsProject.instance().mapLayersByName('stats19')[0]
    b.setLayer(layer)
    b.show()

