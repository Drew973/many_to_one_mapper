from qgis.core import QgsFeatureRequest
from qgis.utils import iface


from . layer_only import layerOnly


'''
class for mapping features of qgis layer to values and vice versa
handles selecting features

'''
#layer and field

class featureMapper(layerOnly):


    def __init__(self,layerBox,fieldBox,prefix=''):
        super(featureMapper,self).__init__(layerBox=layerBox,prefix=prefix)#super calls __init__ of all parent classes

        self.layerBox=layerBox
        self.fieldBox=fieldBox
        self.prefix=prefix
        


    #return features of layer where field=val
    def getFeatures(self,val,check=True):
        layer=self.getLayer()
        field=self.getField()
        
        if layer and field:
            e='%s=%s '%(double_quote(field),single_quote(val))
            request = QgsFeatureRequest().setFilterExpression(e)
            return layer.getFeatures(request)
        

    
#return list of qgis features


   #like getFeatures but returns only 1 feature. displays error messages if not exactly 1 feature
    def getFeature(self,val,check=True):
        feats=self.getFeatures(val)
    
        if not feats:
            iface.messageBar().pushMessage('%s feature with %s=%s does not exist in layer %s'%(self.prefix,self.fieldBox.currentField(),val,self.layerBox.currentLayer().name()),duration=5)
            return

        feats=[f for f in feats]
            
        if len(feats)==0:
            iface.messageBar().pushMessage('%s feature with %s=%s does not exist in layer %s'%(self.prefix,self.fieldBox.currentField(),val,self.layerBox.currentLayer().name()),duration=5)
            return


        if len(feats)>1:
            iface.messageBar().pushMessage('%s multiple features on layer %s with %s = %s'%(self.prefix,self.layerBox.currentLayer().name(),self.fieldBox.currentField(),val),duration=5)
            return

        return feats[0]



    def fidToValue(self,fid,field=None):
        if not field:
            field=self.getField()
            
        feat=self.fidToFeat(fid)
        if feat and field:
            return feat[field]
            

    def fidToValuesList(self,fid,fields):
        feat=self.fidToFeat(fid)
        return [feat[field] for field in fields]

        
    def fidToValuesDict(self,fid,fields):
        feat=self.fidToFeat(fid)
        return {field:feat[field] for field in fields}


#return dict of {field:values} with list of values in order of fids
    def fidsToValues(self,fids,fields):
        r = {field:[] for field in fields}
        
        for fid in fids:
            feat=self.fidToFeat(fid)
            for field in fields:
                r[field].append(feat[field])
            
        return r



    def getSelectedValues(self):
        field=self.getField()
        if field:
            return [f[field] for f in self.getSelectedFeatures()]


    def getSelectedValue(self):
        field=self.getField()
        if field:
            feat=self.getSelectedFeature()
            if feat:
                return feat[field]
        

#set selected features of layer to features where value in vals.
    def selectVals(self,vals):
        field=self.getField()
        layer=self.getLayer()
        
        if field and layer:
            e="%s IN (%s)" %(double_quote(field),','.join([single_quote(v) for v in vals]))
            #expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
            layer.selectByExpression(e)


#set selected features of layer to features where value in vals.
    def valsToFeatures(self,vals):
        field=self.getField()
        layer=self.getLayer()
        
        if field and layer:
            e="%s IN (%s)" %(double_quote(field),','.join([single_quote(v) for v in vals]))
            #expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
            return layer.getFeatures(e)        


#get field.Display error message if not set.    
    def getField(self):
        field=self.fieldBox.currentField()
        if field:
            return field
        else:
             iface.messageBar().pushMessage('%s field not set'%(self.prefix),duration=5)


    def fieldIsSet(self):
        if self.fieldBox.currentField():
            return True
        else:
            return False



    def fieldHasDuplicateValues(self):
        field=self.getField()
        layer=self.getLayer()
        
        if field and layer:
            col_index=layer.dataProvider().fieldNameIndex(field)            
            return len(layer.uniqueValues(col_index))!=len([f for f in layer.getFeatures()])

            
            
            

        

def single_quote(s):
    return "'%s'"%(s)


def double_quote(s):
    return '"%s"'%(s) 


#sects is list of sections.
def select(sects,layer,field,zoom=False):
    
    
    if field: 
        e="%s IN (%s)" %(double_quote(field),','.join([single_quote(s) for s in sects]))#expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
        #Field names in double quotes, string in single quotes
        layer.selectByExpression(e)
        if zoom:
            zoom_to_selected(layer)   
    else:
        iface.messageBar().pushMessage('fitting tool: Field not set.')

        

def zoom_to_selected(layer):
    a=iface.activeLayer()
    iface.setActiveLayer(layer)
    iface.actionZoomToSelected().trigger()
    iface.setActiveLayer(a)
 
