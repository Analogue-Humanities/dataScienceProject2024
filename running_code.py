from impl import MetadataUploadHandler, ProcessDataUploadHandler, ProcessDataQueryHandler, MetadataQueryHandler, \
    AdvancedMashup, BasicMashup

# Once all the classes are imported, first create the relational
# database using the related source data
rel_path = "relational.db"
#process = ProcessDataUploadHandler()
#process.setDbPathOrUrl(rel_path)
#process.pushDataToDb("data/process.json")
# Please remember that one could, in principle, push one or more files
# calling the method one or more times (even calling the method twice
# specifying the same file!)

# Then, create the graph database (remember first to run the
# Blazegraph instance) using the related source data
grp_endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
##metadata = MetadataUploadHandler()
##metadata.setDbPathOrUrl(grp_endpoint)
##metadata.pushDataToDb("data/meta.csv")
# Please remember that one could, in principle, push one or more files
# calling the method one or more times (even calling the method twice
# specifying the same file!)

# In the next passage, create the query handlers for both
# the databases, using the related classes
process_qh = ProcessDataQueryHandler()
process_qh.setDbPathOrUrl(rel_path)

metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl(grp_endpoint)

mashup = AdvancedMashup()

mashup.addProcessHandler(process_qh)
mashup.addMetadataHandler(metadata_qh)

#result_1 = mashup.getAllPeople()
#result_2 = mashup.getEntityById(id = "30")
#result_3 = mashup.getAuthorsOfCulturalHeritageObject(objectId = "30")
#result_4 = mashup.getCulturalHeritageObjectsAuthoredBy(personId="VIAF:100190422")
#result_5 = mashup.getAllActivities()
#result_6 = mashup.getAllActivities()
#result_7 = mashup.getActivitiesByResponsibleInstitution("hilology")
#result_8 = mashup.getActivitiesByResponsiblePerson("Liddell")
#result_9 = mashup.getActivitiesUsingTool("Nikon")
result_10 = mashup.getActivitiesEndedBefore("2024-10-10")

#print(result_2.getTitle())
#print(result_2)
#print(result_3)
#print(len(result_4))
#print(result_6[1])
#print(result_6[1].refersTo.getTitle())
#print(len(result_7))
#res = result_8[0]
#print(res.refersTo.getId())
print(result_10)


