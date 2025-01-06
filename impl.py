# Defining all the necessary classes of the project
from json import load
from pandas import DataFrame, Series, read_csv
from urllib.parse import quote
from sqlite3 import connect
from rdflib import Graph, URIRef, Literal, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import re



# First of all defining Classes of the UML Data Model
class IdentifiableEntity(object):
    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

# The cultural Heritage Object class definition
class CulturalHeritageObject(IdentifiableEntity):
    def __init__(self, title, date, owner,  place, authors):
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
        return

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
    def __init__(self,name):
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
    def __init__(self,technique):
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
    def __init__(self, dbPathOrUrl=""): # The initial value of the dbPathOrUrl
        self.dbPathOrUrl = dbPathOrUrl

    def getDbPathOrUrl(self)-> str:
        return "No URL yet" if self.dbPathOrUrl == "" else str(self.dbPathOrUrl)

    def setDbPathOrUrl(self,DbPath) ->bool: # This method sets or changes the value of the dbPathOrUrl variable
        self.dbPathOrUrl = DbPath
        return True

class UploadHandler(Handler):
#    def __init__(self, dbPathOrUrl, DbPath):
#        super().__init__(dbPathOrUrl)
#        super().setDbPathOrUrl(DbPath)

    def pushDataToDb(self, path: str) -> bool:
        self.path = path

class MetadataUploadHandler(UploadHandler):
    def __init__(self, dbPathOrUrl, DBPath):
        super().__init__(dbPathOrUrl)
        super().setDbPathOrUrl(DBPath)
        super().getDbPathOrUrl()

    def uploadToGrDb(self, graph):

        store = SPARQLUpdateStore()

        # endpoint = 'http://127.0.0.1:9999/blazegraph/sparql'

        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        store.open((endpoint, endpoint))

        for triple in graph.triples((None, None, None)):
            store.add(triple)

        store.close()

        return store

    def pushDataToDb(self, path: str) -> bool:


        myGraph = Graph()

        #IMPORTANT: OR I CAN MAKE A SET IN THE FOR LOOP BELOW TO
        #LAST SOLUTION : TO MAKE A DICTIONARY OUT OF THEM AND MAKE ALL THE VARIABLES INTO STRINGS. AND IT WORKS
        # Classes of Cultural Heritage Objects
        type_classes = {'nauticalChart' : URIRef("https://www.wikidata.org/wiki/Q728502"),
        'printedVolume' : URIRef("https://schema.org/Book"),
        'herbarium' : URIRef("https://www.wikidata.org/wiki/Q181916"),
        'printedMaterial' : URIRef("https://www.wikidata.org/wiki/Q1261026"),
        'specimen' : URIRef("https://www.wikidata.org/wiki/Q85869058"),
        'painting' : URIRef("https://schema.org/Painting"),
        'map' : URIRef("https://schema.org/Map"),
        'manuscriptVolume' : URIRef("https://schema.org/Manuscript"),
        'manuscriptPlate' : URIRef("https://schema.org/Manuscript"),
        'model' : URIRef("https://www.wikidata.org/wiki/Q1979154")}

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

        return MetadataUploadHandler.uploadToGrDb(self, myGraph)


    def makeClassName(self, name: str) ->str:
        n = name.split()
        newClassName = n[0].lower()
        if len(n)>1:
            newClassName = newClassName+n[1].capitalize()
        return newClassName


class ProcessDataUploadHandler(UploadHandler):
    def __init__(self, dbPathOrUrl, DBPath):
        super().__init__(dbPathOrUrl)
        super().setDbPathOrUrl(DBPath)
        super().getDbPathOrUrl()

    def uploadToRelDb(self, data: DataFrame, name: str):
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            return data.to_sql(name, con, if_exists='replace', index = False)

    def pushDataToDb(self, path: str) -> bool:
        with open(path, 'r', encoding='utf-8') as f:
            data = load(f)

        acquisition_records = []
        processing_records = []
        modelling_records = []
        optimising_records = []
        exporting_records = []
        objectIds = []
        rows = []
        activities = set()

        try:
            # Iterate through the list of object
            for item in data:
                objectId = item.get("object id", None)
                objectIds.append(objectId)

                # Ensure the current item is a dictionary and contains "acquisition"
                if isinstance(item, dict) and "acquisition" in item:
                    acquisition = item["acquisition"]
                    # Ensure "acquisition" is a dictionary
                    if isinstance(acquisition, dict):
                        # Add "object id" for context and merge with the acquisition data
                        acquisition_records.append(acquisition)

                # Ensure the current item is a dictionary and contains "processing"
                if isinstance(item, dict) and "processing" in item:
                    processing = item["processing"]
                    # Ensure "processing" is a dictionary
                    if isinstance(processing, dict):
                        processing_records.append(processing)

                # Ensure the current item is a dictionary and contains "modelling"
                if isinstance(item, dict) and "modelling" in item:
                    modelling = item["modelling"]
                    # Ensure "modelling" is a dictionary
                    if isinstance(modelling, dict):
                        modelling_records.append(modelling)

                # Ensure the current item is a dictionary and contains "optimising"
                if isinstance(item, dict) and "optimising" in item:
                    optimising = item["optimising"]
                    # Ensure "optimising" is a dictionary
                    if isinstance(optimising, dict):
                        optimising_records.append(optimising)

                # Ensure the current item is a dictionary and contains "exporting"
                if isinstance(item, dict) and "exporting" in item:
                    exporting = item["exporting"]
                    # Ensure "optimising" is a dictionary
                    if isinstance(exporting, dict):
                        exporting_records.append(exporting)

                if isinstance(item, dict):
                    activities.update(item.keys())
                    activities.discard("object id")

                object_id = item.get("object id", None)
                # Iterate through the dynamically extracted activities
                # And build a list of dictionaries consisting of "object id", "activity", and the "tool" used
                for activity in activities:
                    activity_data = item.get(activity, {})
                    tools = activity_data.get("tool", [])
                    # Handle cases where "tools" may be empty or missing
                    if tools:
                        for tool in tools:
                            rows.append({"object id": object_id, "activity": activity, "tool": tool})
                    else:
                        # Include a row with no tools if the list is empty
                        rows.append({"object id": object_id, "activity": activity, "tool": None})


            df_tools = DataFrame(rows)
            df_tools.dropna(inplace=True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_tools, 'Tools')

            # Adding acquisition records to dataframe
            df_acquisition = DataFrame(acquisition_records)
            df_acquisition.insert(0,"Object Id", Series(objectIds, index = None))
            df_acquisition.insert(6, "activity", "acquisition")
            df_acquisition.drop('tool', axis = 1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_acquisition,'Acquisition')

            # Adding processing records to dataframe
            df_processing = DataFrame(processing_records)
            df_processing.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_processing.insert(5, "activity", "processing")
            df_processing.drop('tool', axis = 1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_processing, 'Processing')

            # Adding modelling records to dataframe
            df_modelling = DataFrame(modelling_records)
            df_modelling.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_modelling.insert(5, "activity", "modelling")
            df_modelling.drop('tool', axis=1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_modelling, 'Modelling')

            # Adding optimising records to dataframe
            df_optimising = DataFrame(optimising_records)
            df_optimising.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_optimising.insert(5, "activity", "optimising")
            df_optimising.drop('tool', axis=1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_optimising, 'Optimising')

            # Adding exporting records to dataframe
            df_exporting = DataFrame(exporting_records)
            df_exporting.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_exporting.insert(5, "activity", "exporting")
            df_exporting.drop('tool', axis=1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_exporting, 'Exporting')

            return True

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

class QueryHandler(Handler):
    pass

class MetadataQueryHandler(QueryHandler):
    pass

class ProcessDataQueryHandler(QueryHandler):
    pass

class BasicMashup:
    pass

class AdvancedMashup(BasicMashup):
    pass
