from datashader.datashape import Categorical

from impl import Handler, MetadataUploadHandler, ProcessDataUploadHandler
from sqlite3 import connect
from pandas import read_sql, DataFrame, concat
from sparql_dataframe import get

# Reading from the sql database, as a sample just a simple query
#with connect('Data.db') as con:
#    query = 'SELECT * FROM Acquisition'
#    df_sql = read_sql(query, con)
#    print(df_sql)
'''
# Reading from the blazegraph, the Graph database, using a simple query as a sample
endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
query2 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://schema.org/>
SELECT ?title
WHERE {
    ?s schema:identifier "2".
  	?s schema:name ?title.
}
"""

df_sparql = get(endpoint, query2, True)
print(df_sparql)
'''
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
            return None


#queryHandler = QueryHandler()
#print(queryHandler.getById("Viadfs"))

class MetadataQueryHandler(QueryHandler):

    def getAllPeople(self) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = """
               PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               PREFIX schema: <https://schema.org/>
               SELECT ?person
               WHERE {
                    ?s schema:author ?authorId.
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
                    SELECT ?id ?objectName
                    WHERE {
                      VALUES ?type {
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
                    ?s rdf:type ?type.
                    ?s schema:identifier ?id.
                    ?s schema:name ?objectName.
                    }
                       """
        df_allCHObjects = get(endpoint, query, True).sort_values(by=["id"])
        return df_allCHObjects

    def getAuthorsOfCulturalHeritageObject(self, personId: str) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f'''
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>              
                SELECT ?author
                WHERE {{
                       ?s schema:identifier "{personId}".
                       ?s schema:author ?authorId.
                       ?authorId schema:name ?author.
                }}
        '''
        df_authorOFCHObject = get(endpoint, query, True)
        if df_authorOFCHObject.empty == False: # Check if the result dataframe is not empty
            return df_authorOFCHObject
        else: # In case the dataframe is empty
            print("There is no author for this object")
            return None

    # Get t
    def getCulturalHeritageObjectsAuthoredBy(self, objectId: str) -> DataFrame:
        endpoint = endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f'''
                       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                       PREFIX schema: <https://schema.org/>              
                       SELECT ?object ?name
                       WHERE {{
                              ?authorId schema:identifier "{objectId}".
                              ?object schema:author ?authorId.
                              ?object schema:name ?name.
                       }}
               '''
        df_objectByAuthor = get(endpoint, query, True)
        if df_objectByAuthor.empty == False:
            return df_objectByAuthor
        else:
            print("There is no objects associated with this author")
            return None


class ProcessDataQueryHandler(QueryHandler):

    # I am not sure if this method is constructed correctly. it is asked to construct a method which returns all the
    # activities. My method is so naive.
    def getAllActivities(self) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = """
                    SELECT activity FROM Acquisition
                     UNION
                    SELECT activity FROM Exporting
                     UNION
                    SELECT activity FROM Modelling 
                     UNION
                    SELECT activity FROM Processing 
                     UNION
                    SELECT activity FROM Optimising 
            """
        df_activities = read_sql(query, con)
        return df_activities

    def getActivitiesByResponsibleInstitution(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT activity FROM Acquisition WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Exporting WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Modelling WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Processing WHERE 'responsible institute' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Optimising WHERE 'responsible institute' LIKE '%{partialName}%'
            """
            df_activityByInstitute = read_sql(query, con)
        return df_activityByInstitute

    def getActivitiesByResponsiblePerson(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT activity FROM Acquisition WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Exporting WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Modelling WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Processing WHERE 'responsible person' LIKE '%{partialName}%'
                     UNION
                    SELECT activity FROM Optimising WHERE 'responsible person' LIKE '%{partialName}%'
            """
            df_activityByPerson = read_sql(query, con)
        return df_activityByPerson

    def getActivitiesUsingTool(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT activity FROM Tools WHERE 'tool' LIKE '%{partialName}%'
            """
            df_activityByTool = read_sql(query, con)
        return df_activityByTool

    def getActivitiesStartedAfter(self, date: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT activity FROM Acquisition WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT activity FROM Exporting WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT activity FROM Modelling WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT activity FROM Processing WHERE 'start date' > '%{date}%'
                     UNION
                    SELECT activity FROM Optimising WHERE 'start date' > '%{date}%'
            """
            df_activityBySD = read_sql(query, con)
        return df_activityBySD

    def getActivitiesEndedBefore(self, date: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT activity FROM Acquisition WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT activity FROM Exporting WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT activity FROM Modelling WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT activity FROM Processing WHERE 'end date' < '%{date}%'
                     UNION
                    SELECT activity FROM Optimising WHERE 'end date' < '%{date}%'
            """
            df_activityBySD = read_sql(query, con)
        return df_activityBySD

    def getAcquisitionsByTechnique(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT 'Object Id', 'responsible institute' FROM Acquisition WHERE technique LIKE '%{partialName}%'
            """




#qu = QueryHandler()
#print(qu.getById("1"))

qh = MetadataQueryHandler()
#print(qh.getAllCulturalHeritageObjects())
#print(qh.getAuthorsOfCulturalHeritageObject("5"))
#print(qh.getCulturalHeritageObjectsAuthoredBy("VIAF:500114874"))

pdqh = ProcessDataQueryHandler()

print(pdqh.getAllActivities())