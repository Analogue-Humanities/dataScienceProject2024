from impl import Handler
from sqlite3 import connect
from pandas import read_sql, DataFrame
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
        endpoint = "http://127.0.0.1:9999/blazegraph/sparql"
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


queryHandler = QueryHandler()
print(queryHandler.getById("Viadfs"))

class MetadataQueryHandler(QueryHandler):

    def getAllPeople(self) -> DataFrame:
        pass

    def getAllCulturalHeritageObjects(self) -> DataFrame:
        pass

    def getAuthorsOfCulturalHeritageObject(self, id: str) -> DataFrame:
        pass

    def getCulturalHeritageObjectsAuthoredBy(self, id: str) -> DataFrame:
        pass

class ProcessDataQueryHandler(QueryHandler):
    pass
