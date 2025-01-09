# Defining all the necessary classes of the project
from json import load
from pandas import DataFrame, read_csv, read_sql, concat
from sqlite3 import connect
from rdflib import Graph, URIRef, Literal, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import re
from sparql_dataframe import get



# First of all defining Classes of the UML Data Model
class IdentifiableEntity(object):
    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

# The cultural Heritage Object class definition
class CulturalHeritageObject(IdentifiableEntity):
    def __init__(self, id, title, date=None, owner=None,  place=None, authors=None):
        super().__init__(id)
        self.title = title
        self.date = date
        self.owner = owner
        self.place = place
        self.authors = authors

    def getTitle(self):
        return self.title

    def getDate(self):
        return self.date

    def getOwner(self):
        return self.owner

    def getPlace(self):
        return self.place

    def getAuthors(self):
        return self.authors

# Defining 10 types of Cultural Heritage Objects classes
class Map(CulturalHeritageObject):
    pass
class Model(CulturalHeritageObject):
    pass

class Painting(CulturalHeritageObject):
    pass

class Specimen(CulturalHeritageObject):
    pass

class Herbarium(CulturalHeritageObject):
    pass

class PrintedMaterial(CulturalHeritageObject):
    pass

class PrintedVolume(CulturalHeritageObject):
    pass

class ManuscriptVolume(CulturalHeritageObject):
    pass

class ManuscriptPlate(CulturalHeritageObject):
    pass

class NauticalChart(CulturalHeritageObject):
    pass


class Person(IdentifiableEntity):
    def __init__(self, name, id=None):
        super().__init__(id)
        self.name = name
    def getName(self):
        return self.name

class Activity(object):
    def __init__(self, institute, person, tool, start, end, refersTo):
        self.institute = institute
        self.person = person
        self.tool = tool
        self.start = start
        self.end = end
        self.refersTo = refersTo

    def getResponsibleInstitute(self):
        return self.institute

    def getResponsiblePerson(self):
        return self.person

    def getTools(self):
        return self.tool

    def getStartDate(self):
        return self.start

    def getEndDate(self):
        return self.end

    def refersTo(self):
        return self.refersTo

class Acquisition(Activity):
    def __init__(self,technique, institute, person, tool, start, end, refersTo):
        super().__init__(institute, person, tool, start, end, refersTo)
        self.technique = technique

    def getTechnique(self):
        return self.technique

class Processing(Activity):
    pass

class Modelling(Activity):
    pass

class Optimising(Activity):
    pass

class Exporting(Activity):
    pass

# Defining operational classes
# First the Handlers
class Handler:
    def __init__(self):
        self.dbPathOrUrl = "" # The initial value of the dbPathOrUrl

    def getDbPathOrUrl(self)-> str:
        return self.dbPathOrUrl

    def setDbPathOrUrl(self,pathOrUrl) ->bool: # This method sets or changes the value of the dbPathOrUrl variable
        self.dbPathOrUrl = pathOrUrl
        return True

class UploadHandler(Handler):
#    def __init__(self, dbPathOrUrl, pathOrUrl):
#        super().__init__()
#        super().setDbPathOrUrl(pathOrUrl)

    def pushDataToDb(self, path: str) -> bool:
        # This is an abstract method
        raise NotImplementedError("Subclasses must implement pushDataToDb")

class MetadataUploadHandler(UploadHandler):
#    def __init__(self, dbPathOrUrl, pathOrUrl):
#        super().__init__()
#        super().setDbPathOrUrl(pathOrUrl)

    def uploadToGrDb(self, graph):

        store = SPARQLUpdateStore()
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        store.open((endpoint, endpoint))

        for s, p, o in graph:
            ask_query = f"ASK {{ <{s}> <{p}> <{o}> }}"
            result = store.query(ask_query)
            if not bool(result):
                store.add((s, p, o))

        store.close()
        return store

    def pushDataToDb(self, path: str) -> bool:

        myGraph = Graph()

        #IMPORTANT: OR I CAN MAKE A SET IN THE FOR LOOP BELOW TO
        #LAST SOLUTION : TO MAKE A DICTIONARY OUT OF THEM AND MAKE ALL THE VARIABLES INTO STRINGS. AND IT WORKS
        # Classes of Cultural Heritage Objects
        type_classes = {'NauticalChart' : URIRef("https://www.wikidata.org/wiki/Q728502"),
        'PrintedVolume' : URIRef("https://schema.org/Book"),
        'Herbarium' : URIRef("https://www.wikidata.org/wiki/Q181916"),
        'PrintedMaterial' : URIRef("https://www.wikidata.org/wiki/Q1261026"),
        'Specimen' : URIRef("https://www.wikidata.org/wiki/Q85869058"),
        'Painting' : URIRef("https://schema.org/Painting"),
        'Map' : URIRef("https://schema.org/Map"),
        'ManuscriptVolume' : URIRef("https://schema.org/Manuscript"),
        'ManuscriptPlate' : URIRef("https://schema.org/Manuscript"),
        'Model' : URIRef("https://www.wikidata.org/wiki/Q1979154")}

        owners = {'BUB' : "https://www.wikidata.org/wiki/Q2901539", # Biblioteca Universitaria di Bologna
        'Sistema Museale di Ateneo di Bologna' : "https://www.wikidata.org/wiki/Q3485343",
        'Biblioteca del Dipartimento di Scienze Biologiche, Geologiche e Ambientali, Bologna' : \
                        "https://www.wikidata.org/wiki/Q112169891",
        'Accademia Carrara' : "https://www.wikidata.org/wiki/Q338367",
        'Orto Botanico ed Herbarium di Bologna' : "https://www.wikidata.org/wiki/Q3133893",
        'Museo di Palazzo Poggi' : "https://www.wikidata.org/wiki/Q3868219",
        'Museo di Storia Naturale di Verona' : "https://www.wikidata.org/wiki/Q3867829"}

        places = {
            'Bologna' : "https://www.wikidata.org/wiki/Q1891",
            'Bergamo' : "https://www.wikidata.org/wiki/Q628",
            'Verona' : "https://www.wikidata.org/wiki/Q2028",
            "Ozzano dell'Emilia" : "https://www.wikidata.org/wiki/Q29080"
        }

        library = "https://schema.org/Library"
        museum = "https://schema.org/Museum"
        city = "https://schema.org/City"

        # Attributes
        id = URIRef("https://schema.org/identifier")
        title = URIRef("https://schema.org/name")
        date = URIRef("https://schema.org/dateCreated")
        name = URIRef("https://schema.org/name")

        # Relation
        author = URIRef("https://schema.org/author")
        owner = URIRef("https://schema.org/owns")
        place = URIRef("https://schema.org/location")

        base_url = "https://github.com/Analogue-Humanities"
        subjects = {}
        types = set()
        authorMapping = {}

        try:
            metaData = read_csv(path,
                                keep_default_na = False,
                                dtype = "string")

            for idx, row in metaData.iterrows():

                objTitle = re.sub(r"[,)(]", "", row['Title']).strip().replace(" ","_")
                subject = URIRef(base_url+"/cHObject/"+objTitle)
                subjects[row['Id']] = subject
                types.update(row['Type'])
                newType = MetadataUploadHandler.makeClassName(self, row['Type'])
                # Add the triples of subject and the type to the Graph
                myGraph.add((subject, RDF.type, type_classes[newType]))
                # Adding the literal names of types as they are in the database
                myGraph.add((type_classes[newType], name, Literal(newType)))

                # Add th triples of subject and id to the Graph
                myGraph.add((subject, id, Literal(row['Id'])))

                # Add the triples of subject and title to the Graph
                myGraph.add((subject, title, Literal(row['Title'].strip())))

                # Add date triples
                myGraph.add((subject, date, Literal(row['Date'])))

                # Extract author's name from the string and check if the authority is VIAF or ULAN
                authorNameVi = re.search(  r"^[^()]*?(?= \(VIAF)", row['Author'])
                authorNameUl = re.search(  r"^[^()]*?(?= \(ULAN)", row['Author'])

                if authorNameVi:
                    authorName = authorNameVi.group()
                    viafId = ''.join(filter(lambda i: i.isdigit(), row['Author']))
                    authorId = URIRef("https://viaf.org/viaf/" + viafId)
                    # Add the Authors and value it's pair of URI to a dictionary to use it later
                    authorMapping[authorName] = authorId
                    myGraph.add((subject, author, authorId))
                    myGraph.add((authorId, id, Literal('VIAF:'+viafId)))
                    myGraph.add((authorId, name, Literal(authorName)))

                elif authorNameUl:
                    authorName = authorNameUl.group()
                    ulanId = ''.join(filter(lambda i: i.isdigit(), row['Author']))
                    authorId = URIRef("http://vocab.getty.edu/page/ulan/" + ulanId)
                    authorMapping[authorName] = authorId

                    myGraph.add((subject, author, authorId))
                    myGraph.add((authorId, id, Literal('ULAN:'+ulanId))) # This will be repeated. make a set and put the operation out of the loop
                    myGraph.add((authorId, name, Literal(authorName)))  # This will be repeated. make a set and put the operation out of the loop

                else:
                    myGraph.add((subject, author, Literal('Unknown')))

                # Produce the RDF of the owner information
                myGraph.add((subject, owner, URIRef(owners[row['Owner']])))

                # Produce and add the RDF for the place information
                myGraph.add((subject, place, URIRef(places[row['Place']])))

            # Produce triple based on owners names and uris
            for k, v in owners.items():
                myGraph.add((URIRef(v), name, Literal(k)))
                ownerId = re.search(r"(Q\d+)", v)

                if ownerId:
                    ownerId = ownerId.group()
                    myGraph.add((URIRef(v), id, Literal(ownerId)))

            myGraph.add((URIRef(owners['BUB']), RDF.type, URIRef(library)))
            myGraph.add((URIRef(owners['Sistema Museale di Ateneo di Bologna']), RDF.type, URIRef(museum)))
            myGraph.add((URIRef(
                owners['Biblioteca del Dipartimento di Scienze Biologiche, Geologiche e Ambientali, Bologna']), RDF.type,
                         URIRef(library)))
            myGraph.add((URIRef(
                owners['Biblioteca del Dipartimento di Scienze Biologiche, Geologiche e Ambientali, Bologna']), RDF.type,
                         URIRef(library)))
            myGraph.add((URIRef(owners['Accademia Carrara']), RDF.type, URIRef(museum)))
            myGraph.add((URIRef(owners['Orto Botanico ed Herbarium di Bologna']), RDF.type, URIRef(museum)))
            myGraph.add((URIRef(owners['Museo di Palazzo Poggi']), RDF.type, URIRef(museum)))
            myGraph.add((URIRef(owners['Museo di Storia Naturale di Verona']), RDF.type, URIRef(museum)))

            #produce triple on place names and uris
            for k, v in places.items():
                myGraph.add((URIRef(v), name, Literal(k)))
                placeId = re.search(r"(Q\d+)", v)

                if placeId:
                    placeId = placeId.group()
                    myGraph.add((URIRef(v), id, Literal(placeId)))

            myGraph.add((URIRef(places['Bologna']), RDF.type, URIRef('https://schema.org/City')))
            myGraph.add((URIRef(places['Bergamo']), RDF.type, URIRef('https://schema.org/City')))
            myGraph.add((URIRef(places['Verona']), RDF.type, URIRef('https://schema.org/City')))
            myGraph.add((URIRef(places["Ozzano dell'Emilia"]), RDF.type, URIRef('https://schema.org/City')))

            MetadataUploadHandler.uploadToGrDb(self, myGraph)
            return True

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def makeClassName(self, name: str) ->str:
        n = name.split()
        newClassName = n[0]
        if len(n)>1:
            newClassName = newClassName+n[1].capitalize()
        return newClassName


class ProcessDataUploadHandler(UploadHandler):
#    def __init__(self, dbPathOrUrl, pathOrUrl):
#        super().__init__()
#        super().setDbPathOrUrl(pathOrUrl)

    def uploadToRelDb(self, data: DataFrame, name: str):
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            return data.to_sql(name, con, if_exists='replace', index = False)

    def pushDataToDb(self, path: str) -> bool:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = load(f)

            activity_mapping = {
                "acquisition": [],
                "processing": [],
                "modelling": [],
                "optimising": [],
                "exporting": []
            }

            tools_data = []  # List to store tool data, because it has several values in the same cell

            for obj in data:
                object_id = obj["object id"]

                for activity_type in activity_mapping:
                    if activity_type in obj:
                        activity_data = obj[activity_type]

                        # Create a unique identifier for each activity
                        activity_id = f"{object_id}_{activity_type}"
                        new_activity = {
                            "activity_id": activity_id,
                            "type": activity_type,
                            "object_id": object_id,
                            "responsible_institute": activity_data.get("responsible institute", ""),
                            "responsible_person": activity_data.get("responsible person", ""),
                            "start_date": activity_data.get("start date", ""),
                            "end_date": activity_data.get("end date", "")
                        }

                        # Add the technique column in case the data is about acquisition
                        if activity_type == "acquisition":
                            new_activity["technique"] = activity_data.get("technique", "")

                        activity_mapping[activity_type].append(new_activity)

                        # Extract tool information and create separate entries
                        for tool in activity_data.get("tool", []):  # iterating through the list of tools
                            tools_data.append({
                                "object_id": object_id,
                                "activity_id": activity_id,
                                "tool_name": tool
                            })

            # Create Dataframe for each activity + tools
            df_acquisition = DataFrame(activity_mapping["acquisition"])
            df_processing = DataFrame(activity_mapping["processing"])
            df_modelling = DataFrame(activity_mapping["modelling"])
            df_optimising = DataFrame(activity_mapping["optimising"])
            df_exporting = DataFrame(activity_mapping["exporting"])
            df_tools = DataFrame(tools_data)

            # Uploading the dataframes to relational database.
            ProcessDataUploadHandler.uploadToRelDb(self, df_tools, 'Tools')
            ProcessDataUploadHandler.uploadToRelDb(self, df_acquisition,'Acquisition')
            ProcessDataUploadHandler.uploadToRelDb(self, df_processing, 'Processing')
            ProcessDataUploadHandler.uploadToRelDb(self, df_modelling, 'Modelling')
            ProcessDataUploadHandler.uploadToRelDb(self, df_optimising, 'Optimising')
            ProcessDataUploadHandler.uploadToRelDb(self, df_exporting, 'Exporting')

            return True

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False


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
        if df_id.empty == False:  # Check if the result dataframe is not empty
            return df_id
        else:  # In case the dataframe is empty
            print("There is no corresponding results for the query")
            return df_id


# queryHandler = QueryHandler()
# print(queryHandler.getById("Viadfs"))

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
            df_personSql = read_sql(query, con).rename(columns={"responsible person": "person"})

        df_persons = concat([df_personSql, df_personGraph], ignore_index=True)
        df_persons = df_persons.drop(df_persons[df_persons["person"] == ""].index)
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
        if df_authorOFCHObject.empty == False:  # Check if the result dataframe is not empty
            return df_authorOFCHObject
        else:  # In case the dataframe is empty
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
                    allActivities.append(activity_class())  # I think we have to fully implement the activity dataframe
                    # and add other parameters ro build the corresponding object
        return allActivities

    def getActivitiesByResponsibleInstitution(self, partialName: str) -> list[Activity]:
        activityByInst = []

        for process_handler in self.processQuery:
            df_activityByInst = process_handler.getActivitiesByResponsibleInstitution(partialName)

            for _, row in df_activityByInst.iterrows():
                activity_class = self.activity_to_class.get(row["activity type"])

                if activity_class:
                    activityByInst.append(activity_class())  # Probably Here also we need some more information.

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
