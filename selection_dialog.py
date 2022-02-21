from PyQt5.QtWidgets import QDialog,QVBoxLayout
from PyQt5.QtGui import QColor


from qgis.gui import QgsColorButton
from qgis.utils import iface



class selectionDialog(QDialog):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))

        self.colorBox = QgsColorButton(self)
        self.colorBox.setAllowOpacity(True)
        self.colorBox.setDefaultColor(QColor(255,0,0,40))
        self.colorBox.setColor(self.colorBox.defaultColor())

        self.layout().addWidget(self.colorBox)

        self.colorBox.colorChanged.connect(self.colorChanged)
        iface.mapCanvas().setSelectionColor( self.colorBox.color())

    def colorChanged(self,color):
        iface.mapCanvas().setSelectionColor(color)
