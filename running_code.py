from impl import ProcessDataQueryHandler, MetadataQueryHandler, AdvancedMashup, ProcessDataUploadHandler, MetadataUploadHandler
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
#metadata = MetadataUploadHandler()
#metadata.setDbPathOrUrl(grp_endpoint)
#metadata.pushDataToDb("data/meta.csv")
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

result_1 = mashup.getAllPeople()
result_2 = mashup.getEntityById(id = "34")
result_3 = mashup.getAuthorsOfCulturalHeritageObject(objectId = "10")
result_4 = mashup.getCulturalHeritageObjectsAuthoredBy(personId="VIAF:100190422")
result_5 = mashup.getAllActivities()
result_6 = mashup.getActivitiesByResponsibleInstitution("hilology")
result_7 = mashup.getAllCulturalHeritageObjects()
result_8 = mashup.getActivitiesByResponsiblePerson("Liddell")
result_9 = mashup.getActivitiesUsingTool("Nikon")
result_10 = mashup.getActivitiesStartedAfter("2023-10-01")
result_11 = mashup.getActivitiesEndedBefore("2023-01-01")
result_12 = mashup.getAcquisitionsByTechnique("3D")
result_13 = mashup.getObjectsHandledByResponsiblePerson("Byron")
result_14 = mashup.getObjectsHandledByResponsibleInstitution("Philology")
result_15 = mashup.getAuthorsOfObjectsAcquiredInTimeFrame("2023-04-15", "2023-04-20")
result_16 = mashup.getActivitiesOnObjectsAuthoredBy("ULAN:500114874")


print(f"All the authors: {result_1}")
print(f"The Entity with the given id: {result_2}")
print(f"The owner of the given object {result_2.getOwner()}")
print(f"All the authors of the given object: {result_3}")
print(f"The title of the first object authored by:{result_4[0].getTitle()}")
print(f"All the activities: {result_5}")
print(f"All the activities by responsible Institution: {result_6}")
print(f"All the Ids of the Cultural Heritage Objects{sorted([int(i.getId()) for i in result_7])}")
print(f"All the activities by responsible person: {result_8}")
print(f"Activities done using the tool: {result_9}")
print(f"First activity started after the date: {result_10[0].getStartDate()}")
print(f"Activities ended before the date: {result_11}")
print(f"Acquisitions done by the technique: {result_12}")
print(f"Objects handled by the responsible person: {result_13}")
print(f"A list of object ids handled by responsible institution: {[i.getId() for i in result_14]}")
print(f"Authors of the objects acquired in time frame: {result_15}")
print(f"Activities done on the objects authored by: {result_16}")

