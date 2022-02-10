from qgis.core import QgsVectorJoinInfo 

#join sections to accidents


accidents = QgsProject.instance().mapLayersByName('stats19')


sections = QgsProject.instance().mapLayersByName('buffers')

print(sections)



joinObject = QgsVectorJoinInfo()

joinObject.joinLayerId = sections.id()#other layer

joinObject.joinFieldName = 'segment_no' #other layer
joinObject.targetFieldName = 'segment_no'#layer
joinObject.memoryCache = True

accidents.addJoin(joinObject)


