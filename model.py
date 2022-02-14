'''
model:


exporting to csv:
    needs to write csv
    for only selected layers and fields


csv:
    header with fieldnames
    field1,list of field2,count



importing csv:
    needs to read csv with field1,list of field2
    layer and field given by ui


ui needs to show feature2 attribute for feature1


each feature_1 mapped to many feature_2
feature 2 can be mapped to many feature_1

many:many


shapefile ids can change.
map features rather than values to avoid problems when layer changed or fields changed


{feature1:[feature2]}?


combination of feature1,layer1,layer2 as key.

'''
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
import csv
import ast

from . import layerFunctions

#from PyQt5.QtCore import pyqtSignal, QObject


class model:


#    dataChanged = pyqtSignal()
    
    def __init__(self):
        self.data = {}#feature:features[]. means can store values for different layers



    #add list of features
    def addFeatures(self,key,features):
        #unique features from list.
        #feature! = feature
        
        def uniqueFeatures(features):
            r = []
            fids = []
            for f in features:
                if not f.id() in fids:
                    r.append(f)
                    fids.append(f.id())
            return r


        if key in self.data:
            self.data[key] = uniqueFeatures(self.data[key]+features)

        else:
            self.data[key] = uniqueFeatures(features)#unique values

        #self.dataChanged.emit()

        

    def removeFeatures(self,key,features):
        self.data[key] = [f for f in self.data[key] if not f in features]
       # self.dataChanged.emit()

    #remove list of rows
    def removeRows(self,key,rows):
        self.data[key] = [f for i,f in enumerate(self.data[key]) if not i in rows]
    #    self.dataChanged.emit()

    def clear(self,key):
        if key in self.data:
            self.data.pop(key)


    def writeCSV(self,file,layer1,field1,layer2,field2):

        print(file,layer1,field1,layer2,field2)
        print(self.data)
        with open(file, 'w') as to:
            to.write('{field1},{field2},Count\n'.format(field1=field1,field2=field2))
            
            for feat in layer1.getFeatures():
                k = key(feat,layer1,layer2)
                if k in self.data:
                    atts2 = [f[field2] for f in self.data[k]]
                    to.write('{att1},"{atts2}",{count}\n'.format(att1=feat[field1],atts2=str(atts2),count=len(atts2)))
                   


    def readCSV(self,file,layer1,field1,layer2,field2):
        with open(file, 'r') as to:
            reader = csv.DictReader(to)
            
            #check fields
            if not field1 in reader.fieldnames:
                raise keyError('file {file} has no field named {f}'.format(file=file,f=field1))

            if not field2 in reader.fieldnames:
                raise keyError('file {file} has no field named {f}'.format(file=file,f=field2))


            self.data = {} # clear existing data
            
            for row in reader:
                f = layerFunctions.getFeature(layer1,field1,row[field1])
                k = key(f,layer1,layer2)
                atts2 = ast.literal_eval(row[field2])

                self.addFeatures(k,[layerFunctions.getFeature(layer2,field2,a) for a in atts2])
                
                   
        



    def fids(self,key,rows=None):
        
        if key in self.data:

            if rows is None:
                return [f.id() for i,f in enumerate(self.data[key])]
            else:
                return [f.id() for i,f in enumerate(self.data[key]) if i in rows]

        return []



    def header(self,field):
        return ['fid',field]

 
#add all accidents within or intersecting geometry of section
#feat is feature for section
    def addWithinGeom(self,feat1,layer1,layer2):
        k = key(feat1,layer1,layer2)
        self.addFeatures(k,layerFunctions.containedFeatures(feat1.geometry(),layer2))


    def addWithinGeomAll(self,layer1,layer2):
        for f in layer1.getFeatures():
            self.addWithinGeom(f,layer1,layer2)
        


        

    #make standardItemModel with featureId and feature[field]
    def toStandardItemModel(self,key,field):
        m = QStandardItemModel()
        m.setHorizontalHeaderLabels(self.header(field))

        if key in self.data:
            rows = len(self.data[key])
            for f in self.data[key]:
                m.appendRow([makeItem(f.id()),makeItem(f[field])])

        return m
        

#creates key from feature and layer.
#using feature directly as key does not work properly. feature != feature ?
def key(feature,layer,layer2):
    if not (feature is None or layer is None or layer2 is None):
        #return tuple(feature.attributes()+[layer.id(),layer2.id()])
        return tuple([feature.id(),layer.id(),layer2.id()])
    #raise ValueError('key({feature},{layer1},{layer2})'.format(feature=feature,layer1=layer,layer2=layer2))


def keyContainsLayer1(key,layer1):
    return key[-1]==layer1.id()


def keyContainsLayer2(key,layer2):
    return key[-2]==layer2.id()
    

def attributeFromKey(key,layer,field):
    i = layer.fields().indexOf(field)
    return key[i]



def makeItem(data):
    item = QtGui.QStandardItem()
    item.setData(data,role=Qt.EditRole )
    return item

        