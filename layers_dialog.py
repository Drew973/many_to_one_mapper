
from PyQt5 import QtWidgets

from qgis.gui import QgsMapLayerComboBox,QgsFieldComboBox

from qgis.core import QgsMapLayerProxyModel
from . widgets import filterableFieldBox


class layersDialog(QtWidgets.QDialog):


    def __init__(self,parent):
        super().__init__(parent)
        
        self.setLayout(QtWidgets.QVBoxLayout(self))

        self.layer1 = QgsMapLayerComboBox(self)
        self.field1 = filterableFieldBox.uniqueFieldBox(self.layer1)
        self.field1.setToolTip('Field to display and include in CSV. Cannot have duplicate values.')
        self.layout().addLayout(toHLayout([QtWidgets.QLabel('Layer 1 and field',self),self.layer1,self.field1]))


        self.layer2 = QgsMapLayerComboBox(self)
        self.field2 = filterableFieldBox.uniqueFieldBox(self.layer2)
        self.field2.setToolTip('Field to display and include in CSV. Cannot have duplicate values.')

        self.layout().addLayout(toHLayout([QtWidgets.QLabel('Layer 2 and field',self),self.layer2,self.field2]))


        self.layer3 = QgsMapLayerComboBox(self)
        self.layer3.setAllowEmptyLayer(True)
        self.layer3.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        
        
        self.field3 = QgsFieldComboBox(self.layer3)
        self.field3.setToolTip('Field matching displayed ')

       
        self.layer3.layerChanged.connect(self.field3.setLayer)
        self.field3.setLayer(self.layer3.currentLayer())
        
        self.label3 = QtWidgets.QLabel('Layer 3 (layer with buffers)',self)
        self.label3.setToolTip('layer with buffers')
        
        self.layout().addLayout(toHLayout([self.label3,self.layer3,self.field3]))
        self.resize(800,250)


def toHLayout(widgets):
    layout = QtWidgets.QHBoxLayout()
    for w in widgets:
        layout.addWidget(w)
    return layout
    
