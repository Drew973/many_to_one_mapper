

from . settings_dialog_base import Ui_Dialog
from PyQt5.QtWidgets import QDialog

class settingsDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self.field1.setLayer(self.layer1.currentLayer())
        self.field2.setLayer(self.layer2.currentLayer())
        self.field3.setLayer(self.layer3.currentLayer())

        self.layer1.layerChanged.connect(self.field1.setLayer)
        self.layer2.layerChanged.connect(self.field2.setLayer)
        self.layer3.layerChanged.connect(self.field3.setLayer)