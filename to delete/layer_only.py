from qgis.core import QgsFeatureRequest
from qgis.utils import iface

'''
class with qgsLayerComboxBox to select layer and methods to act on it

'''

class layerOnly:


    def __init__(self,layerBox,prefix=''):
        self.layerBox=layerBox
        self.prefix=prefix



    def getSelectedFeatures(self):
        layer=self.getLayer()
        if layer:
            return layer.selectedFeatures()

        
    def getSelectedFeature(self):
        layer=self.getLayer()
        
        if layer:
            feats = [f for f in layer.selectedFeatures()]

            if len(feats)==0:
                iface.messageBar().pushMessage('%s no feature selected on %s'%(self.prefix,layer.name()),duration=5)
                return

            if len(feats)>1:
                iface.messageBar().pushMessage('%s multiple features selected on layer %s'%(self.prefix,layer.name()),duration=5)
                return

            return feats[0]


    def fidToFeat(self,fid):
        layer=self.getLayer()
        if layer:
            return layer.getFeature(fid)




    def getAllFeatures(self):
        layer=self.getLayer()
        if layer:
            return layer.getFeatures()




#fids is list of feature ids
    def selectFids(self,fids):
        layer=self.getLayer()
        if layer:
            layer.selectByIds(fids)



    def zoomToSelected(self):
        layer=self.getLayer()
        if layer:
            a=iface.activeLayer()
            iface.setActiveLayer(layer)
            iface.actionZoomToSelected().trigger()
            iface.setActiveLayer(a)



#get layer and display error message if not set.    
    def getLayer(self):
        layer=self.layerBox.currentLayer()
        if layer:
            return layer
        else:
             iface.messageBar().pushMessage('%s layer not set'%(self.prefix),duration=5)
            
