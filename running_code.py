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
result_2 = mashup.getEntityById(id = "31")
result_3 = mashup.getAuthorsOfCulturalHeritageObject(objectId = "28")
result_4 = mashup.getCulturalHeritageObjectsAuthoredBy(personId="VIAF:100190422")
result_5 = mashup.getAllActivities()
result_6 = mashup.getAllActivities()
result_7 = mashup.getActivitiesByResponsibleInstitution("hilology")
result_8 = mashup.getActivitiesByResponsiblePerson("Liddell")
result_9 = mashup.getActivitiesUsingTool("Nikon")
result_10 = mashup.getActivitiesStartedAfter("2023-10-01")
result_11 = mashup.getActivitiesEndedBefore("2023-01-01")
result_12 = mashup.getAcquisitionsByTechnique("3D")
result_13 = mashup.getObjectsHandledByResponsiblePerson("Byron")
result_14 = mashup.getObjectsHandledByResponsibleInstitution("Philology")
result_15 = mashup.getAuthorsOfObjectsAcquiredInTimeFrame("2023-04-15", "2023-04-20")
result_16 = mashup.getActivitiesOnObjectsAuthoredBy("ULAN:500114874")
result_17 = mashup.getAllCulturalHeritageObjects()

print(result_1)
print(result_2)
print(result_2)
print(result_3)
print(result_4)
print(f"result_5{result_5}")
print(len(result_5))
print(len(result_7))
res = result_8
print(res)
print(result_10[0].getStartDate())
print(result_11)
print(result_12)
print(result_13)
print([i.getId() for i in result_14])
for i in result_15:
    print(i.getId())
print(result_16)
print(f"Here is all cultural heritage objects:\n {result_17}")
print(sorted([int(i.getId()) for i in result_17]))
