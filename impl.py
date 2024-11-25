# Defining all the necessary classes of the project
from json import load
from pandas import DataFrame, Series, read_csv
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
        return "No URL yet" if  self.dbPathOrUrl == "" else str(self.dbPathOrUrl)

    def setDbPathOrUrl(self,DbPath) ->bool: #This method sets or changes the value of the dbPathOrUrl variable
        self.dbPathOrUrl = DbPath
        return True

class UploadHandler(Handler):
    def pushDataToDb(self, path: str) -> bool:
        pass

class MetadataUploadHandler(UploadHandler):
 #  def __init__(self):
 #      super().__init__(self,dbPathOrUrl)
 #       super().getDbPathOrUrl()
 #       super().setDbPathOrUrl(DbPath)

    def uploadToGrDb(self, data, name):
        pass

    def pushDataToDb(self, path: str) -> bool:

        myGraph = Graph()

        #IMPORTANT: OR I CAN MAKE A SET IN THE FOR LOOP BELOW TO
        # Classes of Cultural Heritage Objects
        nauticalChart = URIRef("https://www.wikidata.org/wiki/Q728502")
        printedVolume = URIRef("https://schema.org/Book")
        herbarium = URIRef("https://www.wikidata.org/wiki/Q181916")
        printedMaterial = URIRef("https://www.wikidata.org/wiki/Q1261026")
        specimen = URIRef("https://www.wikidata.org/wiki/Q85869058")
        painting = URIRef("https://schema.org/Painting")
        map = URIRef("https://schema.org/Map")
        manuscriptVolume = URIRef("https://schema.org/Manuscript")
        manuscriptPlate= URIRef("https://schema.org/Manuscript")
        model = URIRef("https://www.wikidata.org/wiki/Q1979154")

        # Attributes
        id = URIRef("")
        type = URIRef("")
        title = URIRef("")
        date = URIRef("")
        author = URIRef("")
        owner = URIRef("")
        place = URIRef("")



        base_url = "https://github.com/Analogue-Humanities"
        subjects = {}

        metaData = read_csv(path,
                            keep_default_na = False,
                            dtype = "string")

        for idx, row in metaData.iterrows():

            title = re.sub(r"[,)(]", "", row['Title']).strip().replace(" ","_")
            subject = URIRef(base_url+"cHObject"+title)
            subjects[row['Id']] = subject

            if row['Type'] == 'Nautical chart':
                myGraph.add((subject, RDF.type, nauticalChart))


class ProcessDataUploadHandler(UploadHandler):
    def __init__(self):
        super().__init__(dbPathOrUrl)
        super().getDbPathOrUrl()
        super().setDbPathOrUrl(DbPath)

    def uploadToRelDb(self, data: DataFrame, name: str):
        with connect('Data.db') as con:
            return data.to_sql(name, con, if_exists='replace', index = False)

    def pushDataToDb(self, path: str) -> bool:
#    try:
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
            df_acquisition.drop('tool', axis = 1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_acquisition,'Acquisition')

            # Adding processing records to dataframe
            df_processing = DataFrame(processing_records)
            df_processing.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_processing.drop('tool', axis = 1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_processing, 'Processing')

            # Adding modelling records to dataframe
            df_modelling = DataFrame(modelling_records)
            df_modelling.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_modelling.drop('tool', axis=1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_modelling, 'Modelling')

            # Adding optimising records to dataframe
            df_optimising = DataFrame(optimising_records)
            df_optimising.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
            df_optimising.drop('tool', axis=1, inplace = True)
            ProcessDataUploadHandler.uploadToRelDb(self, df_optimising, 'optimising')

            # Adding exporting records to dataframe
            df_exporting = DataFrame(exporting_records)
            df_exporting.insert(0,"Object Id", Series(objectIds, index = None, dtype = str))
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
