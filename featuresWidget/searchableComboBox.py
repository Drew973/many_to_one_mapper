
from PyQt5.QtWidgets import QComboBox,QCompleter


#validator is for editing items etc.
class searchableComboBox(QComboBox):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
       # self.setCompleter(QCompleter(self.model(),self))
      #  self.completer().setCompletionMode(QCompleter.PopupCompletion)

         
    #set edit text to current item text when focused out.
    def focusOutEvent(self,e):
        super().focusOutEvent(e)
        self.setEditText(self.currentValue())
    
    
    def currentValue(self):
        return self.itemText(self.currentIndex())
    
    
if __name__=='__console__':
    w = searchableComboBox()
    w.insertItems(0,['1','2','3','40','50'])
    w.show()
    