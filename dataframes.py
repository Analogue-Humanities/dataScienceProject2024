from datashader.datashape import Categorical

from impl import (Handler, MetadataUploadHandler, ProcessDataUploadHandler, IdentifiableEntity, Person,
                  CulturalHeritageObject, Activity, Acquisition, Map, Model, PrintedMaterial, PrintedVolume,
                  ManuscriptVolume, ManuscriptPlate, NauticalChart, Painting, Specimen, Herbarium, Exporting, Modelling,
                  Optimising)
from sqlite3 import connect
from pandas import read_sql, DataFrame, concat
from sparql_dataframe import get

# I implement the remaining classes here in order to avoid several uploads to th egraph database. when completed I will
# merge them all.


class QueryHandler(Handler):
    def __init__(self):
        self.id = id

    def getById(self, id: str) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        SELECT ?title
        WHERE {{
            ?s schema:identifier "{id}".
            ?s schema:name ?title.
        }}
        """
        df_id = get(endpoint, query, True)
        if df_id.empty == False: # Check if the result dataframe is not empty
            return df_id
        else: # In case the dataframe is empty
            print("There is no corresponding results for the query")
            return df_id


#queryHandler = QueryHandler()
#print(queryHandler.getById("Viadfs"))

class MetadataQueryHandler(QueryHandler):

    def getAllPeople(self) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = """
               PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               PREFIX schema: <https://schema.org/>
               SELECT ?id ?person
               WHERE {
                    ?s schema:author ?authorId.
                    ?authorId schema:identifier ?id.
                    ?authorId schema:name ?person.
               }
               """
        df_personGraph = get(endpoint, query, True)

        # Reading the sql file and querying from 5 tables the column corresponding to person, renaming the column label and
        # concatenating it with the dataframe extracted from Graph dataframe
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = '''SELECT "responsible person" FROM Acquisition
                     UNION
                     SELECT "responsible person" FROM Exporting
                     UNION
                     SELECT "responsible person" FROM Modelling
                     UNION
                     SELECT "responsible person" FROM Processing
                     UNION
                     SELECT "responsible person" FROM Optimising'''
            df_personSql = read_sql(query, con).rename(columns={"responsible person":"person"})

        df_persons = concat([df_personSql, df_personGraph], ignore_index=True)
        df_persons = df_persons.drop(df_persons[df_persons["person"] ==""].index)
        df_persons = df_persons.reset_index(drop=True)
        return df_persons

    def getAllCulturalHeritageObjects(self) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX schema: <https://schema.org/>
                    PREFIX wikidata: <https://www.wikidata.org/wiki/>
                    SELECT ?id ?objectName ?type ?author
                    WHERE {
                      VALUES ?typeId {
                        wikidata:Q728502
                        schema:Book
                        wikidata:Q181916
                        wikidata:Q1261026
                        wikidata:Q85869058
                        schema:Painting
                        schema:Map
                        schema:Manuscript
                        wikidata:Q1979154 
                      }   
                    ?s rdf:type ?typeId.
                    ?s schema:identifier ?id.
                    ?s schema:name ?objectName.
                    ?typeId schema:name ?type.
                    ?s schema:author ?authorId.
                    ?authorId schema:name ?author.
                    }
                       """
        df_allCHObjects = get(endpoint, query, True).sort_values(by=["id"])
        return df_allCHObjects

    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f'''
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>              
                SELECT ?author
                WHERE {{
                       ?s schema:identifier "{objectId}".
                       ?s schema:author ?authorId.
                       ?authorId schema:name ?author.
                }}
        '''
        df_authorOFCHObject = get(endpoint, query, True)
        if df_authorOFCHObject.empty == False: # Check if the result dataframe is not empty
            return df_authorOFCHObject
        else: # In case the dataframe is empty
            print("There is no author for this object")
            return df_authorOFCHObject

    # Get the Objects from the author input
    def getCulturalHeritageObjectsAuthoredBy(self, personId: str) -> DataFrame:
        endpoint = endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f'''
                       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                       PREFIX schema: <https://schema.org/>              
                       SELECT ?object ?name
                       WHERE {{
                              ?authorId schema:identifier "{personId}".
                              ?object schema:author ?authorId.
                              ?object schema:name ?name.
                       }}
               '''
        df_objectByAuthor = get(endpoint, query, True)
        if df_objectByAuthor.empty == False:
            return df_objectByAuthor
        else:
            print("There is no objects associated with this author")
            return df_objectByAuthor


class ProcessDataQueryHandler(QueryHandler):

    # I am not sure if this method is constructed correctly. it is asked to construct a method which returns all the
    # activities. My method is so naive.
    # Update: I think I have to SELECT other columns from the database too. Because it makes no sense. to have only
    # a list of four activities.
    def getAllActivities(self) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = """
                    SELECT 'activity type' FROM Acquisition
                     UNION
                    SELECT 'activity type' FROM Exporting
                     UNION
                    SELECT 'activity type' FROM Modelling 
                     UNION
                    SELECT 'activity type' FROM Processing 
                     UNION
                    SELECT 'activity type' FROM Optimising 
            """
        df_activities = read_sql(query, con)
        return df_activities

    def getActivitiesByResponsibleInstitution(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'activity type' FROM Acquisition WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Exporting WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Modelling WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Processing WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Optimising WHERE 'responsible institute' LIKE '%{partialName}%'
            """
            df_activityByInstitute = read_sql(query, con)
        return df_activityByInstitute

    def getActivitiesByResponsiblePerson(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'activity type' FROM Acquisition WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Exporting WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Modelling WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Processing WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT 'activity type' FROM Optimising WHERE 'responsible person' LIKE '%{partialName}%'
            """
            df_activityByPerson = read_sql(query, con)
        return df_activityByPerson

    def getActivitiesUsingTool(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'activity type' FROM Tools WHERE 'tool' LIKE '%{partialName}%'
            """
            df_activityByTool = read_sql(query, con)
        return df_activityByTool

    def getActivitiesStartedAfter(self, date: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'activity type' FROM Acquisition WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Exporting WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Modelling WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Processing WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Optimising WHERE 'start date' > '%{date}%'
            """
            df_activityBySD = read_sql(query, con)
        return df_activityBySD

    def getActivitiesEndedBefore(self, date: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'activity type' FROM Acquisition WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Exporting WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Modelling WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Processing WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT 'activity type' FROM Optimising WHERE 'end date' < '%{date}%'
            """
            df_activityBySD = read_sql(query, con)
        return df_activityBySD

    def getAcquisitionsByTechnique(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'Object Id', 'responsible institute' FROM Acquisition WHERE technique LIKE '%{partialName}%'
            """
            df_acquisitionByTech = read_sql(query, con)
        return df_acquisitionByTech

class BasicMashup:
    def __init__(self):
        self.metadataQuery = list()
        self.processQuery = list()

        # Mapping of types to their corresponding classes to construct related classes dynamically
        self.type_to_class = {
            "Map": Map,
            "Model": Model,
            "Painting": Painting,
            "Specimen": Specimen,
            "Herbarium": Herbarium,
            "PrintedMaterial": PrintedMaterial,
            "PrintedVolume": PrintedVolume,
            "ManuscriptVolume": ManuscriptVolume,
            "ManuscriptPlate": ManuscriptPlate,
            "NauticalChart": NauticalChart,
        }

        # Mapping the activities to their corresponding classes

        self.activity_to_class = {
            "acquisition": Acquisition,
            "exporting": Exporting,
            "modelling": Modelling,
            "optimising": Optimising
        }

    def cleanMetadataHandlers(self) -> bool:
        try:
            self.metadataQuery.clear()
            return True
        except:
            return False

    def cleanProcessHandlers(self) -> bool:
        try:
            self.processQuery.clear()
            return True
        except:
            return False

    def addMetadataHandler(self, handler: MetadataQueryHandler) -> bool:
        try:
            self.metadataQuery.append(handler)
            return True
        except:
            return False

    def addProcessHandler(self, handler: ProcessDataQueryHandler) -> bool:
        try:
            self.processQuery.append(handler)
            return True
        except:
            return False

    def getEntityById(self, id: str) -> IdentifiableEntity or None:

        for metadata_handler in self.metadataQuery:
            # Query for Cultural Heritage Objects
            df_ch_objects = metadata_handler.getAllCulturalHeritageObjects()
            match = df_ch_objects[df_ch_objects["id"] == id]
            if not match.empty:
                row = match.iloc[0]

                # Dynamically construct the object based on the type
                entity_class = self.type_to_class.get(row["type"])
                if entity_class:
                    return entity_class(id=row["id"], title=row["objectName"])

            # Query for person
            df_people = metadata_handler.getAllPeople()
            match = df_people[df_people["id"] == id]
            if not match.empty:
                row = match.iloc[0]
                return Person(id=row["id"], name=row["person"])

        # If no match is found
        return None

    def getAllPeople(self) -> list[Person]:
        allPeople = []
        # Iterate through all MetadataQueryHandler objects
        # Although there should be one object in the list
        for metadata_handler in self.metadataQuery:
            # Getting the dataframe of the all people
            df_people = metadata_handler.getAllPeople()

            # Convert the data of each row and to the object Person and add them to the list
            for _, row in df_people.iterrows():
                person = Person(id=row["id"], name=row["person"])
                allPeople.append(person)

        return allPeople

    def getAllCulturalHeritageObjects(self) -> list[CulturalHeritageObject]:
        allCHObjects = []

        # Next is just like the previous method. except for the get method from the MetaDataQueryHandler class
        for metadata_handler in self.metadataQuery:
            df_CHObjects = metadata_handler.getAllCulturalHeritageObjects()

            for _, row in df_CHObjects.iterrows():
                # Dynamically construct the object based on the type
                entity_class = self.type_to_class.get(row["type"])

                if entity_class:
                    allCHObjects.append(entity_class(id=row["id"], title=row["objectName"], authors=row["author"]))

        return allCHObjects

    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> list[Person]:
        allAuthors = []

        for metadata_handler in self.metadataQuery:
            df_authors = metadata_handler.getAuthorsOfCulturalHeritageObject(objectId)

            for _, row in df_authors.iterrows():
                author = Person(id=row["id"], name=row["person"])
                allAuthors.append(author)

        return allAuthors

    def getCulturalHeritageObjectsAuthoredBy(self, personId: str) -> list[CulturalHeritageObject]:
        CHObjects = []

        for metadata_handler in self.metadataQuery:
            df_CHObjects = metadata_handler.getCulturalHeritageObjectsAuthoredBy(personId)

            for _, row in df_CHObjects.iterrows():
                entity_class = self.type_to_class.get(row["type"])

                if entity_class:
                    CHObjects.append(entity_class(id=row["id"], title=row["objectName"], authors=row["author"]))

        return CHObjects

    def getAllActivities(self) -> list[Activity]:
        allActivities = []

        # Iterate through the list of Process Query objects (Like metadata query objects)
        for process_handler in self.processQuery:
            df_allActivities = process_handler.getAllActivities()

            for _, row in df_allActivities.iterrows():
                activity_class = self.activity_to_class.get(row["activity type"])

                if activity_class:
                    allActivities.append(activity_class()) # I think we have to fully implement the activity dataframe
                    # and add other parameters ro build the corresponding object
        return allActivities

    def getActivitiesByResponsibleInstitution(self, partialName: str) -> list[Activity]:
        activityByInst = []

        for process_handler in self.processQuery:
            df_activityByInst = process_handler.getActivitiesByResponsibleInstitution(partialName)

            for _, row in df_activityByInst.iterrows():
                activity_class = self.activity_to_class.get(row["activity type"])

                if activity_class:
                    activityByInst.append(activity_class()) # Probably Here also we need some more information.
            
        return activityByInst

    def getActivitiesByResponsiblePerson(self, partialName: str) -> list[Activity]:
        activityByPers = []

        for process_handler in self.processQuery:
            df_activityByPers = process_handler.getActivitiesByResponsiblePerson(partialName)

            for _, row in df_activityByPers.iterrows():
                activity_class = self.activity_to_class.get(row["activity type"])

                if activity_class:
                    activityByPers.append(activity_class())  # Probably Here also we need some more information.

        return activityByPers

    def getActivitiesUsingTool(self, partialName: str) -> list[Activity]:
        pass

    def getActivitiesStartedAfter(self, date: str) -> list[Activity]:
        pass

    def getActivitiesEndedBefore(self, date: str) -> list[Activity]:
        pass

    def getAcquisitionsByTechnique(self, partialName: str) -> list[Acquisition]:
        pass



class AdvancedMashup(BasicMashup):
    def getActivitiesOnObjectsAuthoredBy(self, personId: str) -> list[Activity]:
        pass

    def getObjectsHandledByResponsiblePerson(self, partialName: str) -> list[CulturalHeritageObject]:
        pass

    def getObjectsHandledByResponsibleInstitution(self, partialName: str) -> list[CulturalHeritageObject]:
        pass

    def getAuthorsOfObjectsAcquiredInTimeFrame(self, start: str, end: str) -> list[Person]:
        pass

#qu = QueryHandler()
#print(qu.getById("1"))

qh = MetadataQueryHandler()
#print(qh.getAllCulturalHeritageObjects())
#print(qh.getAuthorsOfCulturalHeritageObject("5"))
#print(qh.getCulturalHeritageObjectsAuthoredBy("VIAF:500114874"))

pdqh = ProcessDataQueryHandler()

print(pdqh.getAllActivities())