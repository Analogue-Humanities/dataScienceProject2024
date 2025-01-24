from json import load
from pandas import DataFrame, read_csv, read_sql
from sqlite3 import connect
from rdflib import Graph, URIRef, Literal, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import re
from sparql_dataframe import get

# Define the classes of the UML Data Model
class IdentifiableEntity(object):
    def __init__(self, id: str):
        self.id = id

    def getId(self) -> str:
        return self.id

# The cultural Heritage Object class definition
class CulturalHeritageObject(IdentifiableEntity):
    def __init__(self, id, title, date, owner,  place, author):
        super().__init__(id)
        self.title = title
        self.date = date
        self.owner = owner
        self.place = place
        self._authors = [Person(name = author["authorName"][i],
                                id = author["authorId"][i]) for i in range(len(author["authorName"]))]

    def getTitle(self):
        return self.title

    def getDate(self):
        return self.date

    def getOwner(self):
        return self.owner

    def getPlace(self):
        return self.place

    def getAuthors(self):
        return self._authors

# Define 10 types of Cultural Heritage Objects classes
class Map(CulturalHeritageObject):
    def __repr__(self):
        return f"Map(Id: '{self.id}', Title: '{self.title}')"

class Model(CulturalHeritageObject):
    def __repr__(self):
        return f"Model(Id: '{self.id}', Title: '{self.title}')"

class Painting(CulturalHeritageObject):
    def __repr__(self):
        return f"Painting(Id: '{self.id}', Title: '{self.title}')"

class Specimen(CulturalHeritageObject):
    def __repr__(self):
        return f"Specimen(Id: '{self.id}', Title: '{self.title}')"

class Herbarium(CulturalHeritageObject):
    def __repr__(self):
        return f"Herbarium(Id: '{self.id}', Title: '{self.title}')"

class PrintedMaterial(CulturalHeritageObject):
    def __repr__(self):
        return f"PrintedMaterial(Id: '{self.id}', Title: '{self.title}')"

class PrintedVolume(CulturalHeritageObject):
    def __repr__(self):
        return f"PrintedVolume(Id: '{self.id}', Title: '{self.title}')"

class ManuscriptVolume(CulturalHeritageObject):
    def __repr__(self):
        return f"ManuscriptVolume(Id: '{self.id}', Title: '{self.title}')"

class ManuscriptPlate(CulturalHeritageObject):
    def __repr__(self):
        return f"ManuscriptPlate(Id: '{self.id}', Title: '{self.title}')"

class NauticalChart(CulturalHeritageObject):
    def __repr__(self):
        return f"NauticalChart(Id: '{self.id}', Title: '{self.title}')"

# Define Person class
class Person(IdentifiableEntity):
    def __init__(self, name, id=None):
        super().__init__(id)
        super().getId()
        self.name = name

    def __repr__(self):
        return f"Person(Name: '{self.name}', Id: '{self.id}')"
    def getName(self):
        return self.name

class Activity(object):
    def __init__(self, institute, person, tool, start, end, cultural_heritage_object):
        self.institute = institute
        self.person = person
        self.tool = set()
        for i in tool:
            self.tool.add(i)
        self.start = start
        self.end = end
        self._cultural_heritage_object = cultural_heritage_object

    def getResponsibleInstitute(self) -> str:
        return self.institute

    def getResponsiblePerson(self)  -> str or None:
        if self.person:
            return self.person
        else:
            return None

    def getTools(self) -> set:
        return self.tool

    def getStartDate(self) -> str or None:
        if self.start:
            return self.start
        else:
            return None

    def getEndDate(self) -> str or None:
        if self.end:
            return self.end
        else:
            return None

    def refersTo(self) -> CulturalHeritageObject:
        return self._cultural_heritage_object

class Acquisition(Activity):
    def __init__(self,technique, institute, person, tool, start, end, cultural_heritage_object):
        super().__init__(institute, person, tool, start, end, cultural_heritage_object)
        self.technique = technique

    def __repr__(self):
        return f"Acquisition[RefersTo Object:**'{self._cultural_heritage_object}'**]"

    def getTechnique(self) -> str:
        return self.technique

class Processing(Activity):
    def __repr__(self):
        return f"Processing[RefersTo Object:**'{self._cultural_heritage_object}'**]"

class Modelling(Activity):
    def __repr__(self):
        return f"Modelling[RefersTo Object:**'{self._cultural_heritage_object}'**]"

class Optimising(Activity):
    def __repr__(self):
        return f"Optimising[RefersTo Object:**'{self._cultural_heritage_object}'**]"

class Exporting(Activity):
    def __repr__(self):
        return f"Exporting[RefersTo Object:**'{self._cultural_heritage_object}'**]"

# Define the handlers for reading the input data, cleaning it and upload them to database
class Handler:
    def __init__(self, dbPathOrUrl=""):
        self.dbPathOrUrl = dbPathOrUrl # The initial value of the dbPathOrUrl

    def getDbPathOrUrl(self)-> str:
        return self.dbPathOrUrl

    def setDbPathOrUrl(self,pathOrUrl) ->bool: # This method sets or changes the value of the dbPathOrUrl variable
        self.dbPathOrUrl = pathOrUrl
        return True

class UploadHandler(Handler):

    def pushDataToDb(self, path: str) -> bool:
        # This is an abstract method
        raise NotImplementedError("Subclasses must implement pushDataToDb")

class MetadataUploadHandler(UploadHandler):

    def uploadToGrDb(self, graph):

        store = SPARQLUpdateStore()
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        store.open((endpoint, endpoint))

        for triple in graph.triples((None, None, None)):
            # Check if the triple already exists
            query = f"ASK {{ {triple[0].n3()} {triple[1].n3()} {triple[2].n3()} }}"  # Construct the ASK query
            result = store.query(query)

            if not bool(result):  # If the triple doesn't exist, add it
                store.add(triple)

        store.close()
        return store

    def pushDataToDb(self, path: str) -> bool:

        myGraph = Graph()

        # Classes of Cultural Heritage Objects
        type_classes = {'NauticalChart' : "https://www.wikidata.org/wiki/Q728502",
        'PrintedVolume' : "https://schema.org/Book",
        'Herbarium' : "https://www.wikidata.org/wiki/Q181916",
        'PrintedMaterial' : "https://www.wikidata.org/wiki/Q1261026",
        'Specimen' : "https://www.wikidata.org/wiki/Q85869058",
        'Painting' : "https://schema.org/Painting",
        'Map' : "https://schema.org/Map",
        'ManuscriptVolume' : "https://schema.org/ArchiveComponent",
        'ManuscriptPlate' : "https://schema.org/Manuscript",
        'Model' : "https://www.wikidata.org/wiki/Q1979154"}

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

        base_url = "https://github.com/Analogue-Humanities"

        library = "https://schema.org/Library"
        museum = "https://schema.org/Museum"
        city = "https://schema.org/City"
        unknown = base_url+"/Unknown"
        person = "https://schema.org/Person"

        # Attributes
        id = URIRef("https://schema.org/identifier")
        title = URIRef("https://schema.org/name")
        date = URIRef("https://schema.org/dateCreated")
        name = URIRef("https://schema.org/name")

        # Relation
        author = URIRef("https://schema.org/author")
        owner = URIRef("https://schema.org/owns")
        place = URIRef("https://schema.org/location")

        # Linnaeus VIAF which was not in the source file is added to the database
        Linnaeus_id = "VIAF:34594730"
        parenthesis_Pattern = re.compile(r"\(.*?\)")

        try:
            metaData = read_csv(path,
                                keep_default_na = False,
                                dtype = "string")

            for idx, row in metaData.iterrows():

                # Some data cleansing work
                if row["Author"] == "":
                    in_row_author = re.search(r'\((.*?),', row["Title"])
                    if in_row_author and in_row_author.group(1) == "Linnaeus":
                        metaData.loc[idx, "Author"] = in_row_author.group(1) + f" ({Linnaeus_id})"

                if row["Date"] == "":
                    in_row_date = re.search(r'\d+', row["Title"])
                    if in_row_date:
                        metaData.loc[idx, "Date"] = in_row_date.group(0)

                if parenthesis_Pattern.search(row["Title"]):
                    metaData.loc[idx, "Title"] = parenthesis_Pattern.sub("", row["Title"]).strip()

                # Updating the dataframe with the cleansed data
                row["Author"] = metaData.loc[idx, "Author"]
                row["Date"] = metaData.loc[idx, "Date"]
                row["Title"] = metaData.loc[idx, "Title"].strip()

                objTitle = row["Title"].replace(" ","_")
                subject = URIRef(base_url+"/cHObject/"+row["Id"]+"_"+objTitle)

                newType = MetadataUploadHandler.makeClassName(self, row['Type'])
                # Add the triples of subject and the type to the Graph
                myGraph.add((subject, RDF.type, URIRef(type_classes[newType])))

                # Adding the literal names of types as they are in the database
                if (URIRef(type_classes[newType]), name, Literal(newType)) not in myGraph:
                    myGraph.add((URIRef(type_classes[newType]), name, Literal(newType)))

                # Add th triples of subject and id to the Graph
                myGraph.add((subject, id, Literal(row['Id'])))

                # Add the triples of subject and title to the Graph
                myGraph.add((subject, title, Literal(row['Title'])))

                # Add date triples
                myGraph.add((subject, date, Literal(row['Date'])))

                # Produce the RDF of the owner information
                myGraph.add((subject, owner, URIRef(owners[row['Owner']])))

                # Produce and add the RDF for the place information
                myGraph.add((subject, place, URIRef(places[row['Place']])))

                all_authors = row['Author'].split("; ") # Separate the authors in case there are more than one author

                for auth in all_authors:

                    # Extract author's name from the string and check if the authority is VIAF or ULAN
                    authorNameVi = re.search(  r"^[^()]*?(?= \(VIAF)", auth)
                    authorNameUl = re.search(  r"^[^()]*?(?= \(ULAN)", auth)

                    if authorNameVi:
                        authorName = authorNameVi.group()
                        viafId = ''.join(filter(lambda i: i.isdigit(), auth))
                        authorId = URIRef("https://viaf.org/viaf/" + viafId)

                        myGraph.add((subject, author, authorId))

                        if (authorId, id, Literal('VIAF:'+viafId)) not in myGraph:
                            myGraph.add((authorId, id, Literal('VIAF:'+viafId)))

                        if (authorId, name, Literal(authorName)) not in myGraph:
                            myGraph.add((authorId, name, Literal(authorName)))

                        if (authorId, RDF.type, URIRef(person)) not in myGraph:
                            myGraph.add((authorId, RDF.type, URIRef(person)))

                    elif authorNameUl:
                        authorName = authorNameUl.group()
                        ulanId = ''.join(filter(lambda i: i.isdigit(), auth))
                        authorId = URIRef("http://vocab.getty.edu/page/ulan/" + ulanId)

                        myGraph.add((subject, author, authorId))

                        if (authorId, id, Literal('ULAN:'+ulanId)) not in myGraph:
                            myGraph.add((authorId, id, Literal('ULAN:'+ulanId)))

                        if (authorId, name, Literal(authorName)) not in myGraph:
                            myGraph.add((authorId, name, Literal(authorName)))

                        if (authorId, RDF.type, URIRef(person)) not in myGraph:
                            myGraph.add((authorId, RDF.type, URIRef(person)))

                    else:
                        myGraph.add((subject, author, URIRef(unknown))) # In case there were no value for author

            myGraph.add((URIRef(unknown), name, Literal("Unknown"))) # Add name and id of the unknown to be consistent
            myGraph.add((URIRef(unknown), id, Literal("Unknown")))

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

            myGraph.add((URIRef(places['Bologna']), RDF.type, URIRef(city)))
            myGraph.add((URIRef(places['Bergamo']), RDF.type, URIRef(city)))
            myGraph.add((URIRef(places['Verona']), RDF.type, URIRef(city)))
            myGraph.add((URIRef(places["Ozzano dell'Emilia"]), RDF.type, URIRef(city)))

            MetadataUploadHandler.uploadToGrDb(self, myGraph)
            return True

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def makeClassName(self, name: str) ->str:
        newClassName = ""
        n = name.split()
        for i in n:
            newClassName += i.capitalize()

        return newClassName

class ProcessDataUploadHandler(UploadHandler):

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
                            "end_date": activity_data.get("end date", ""),
                            "tool": "; ".join(activity_data.get("tool", ""))
                        }

                        # Add the technique column in case the data is about acquisition
                        if activity_type == "acquisition":
                            new_activity["technique"] = activity_data.get("technique", "")

                        activity_mapping[activity_type].append(new_activity)


            # Create Dataframe for each activity + tools
            df_acquisition = DataFrame(activity_mapping["acquisition"])
            df_processing = DataFrame(activity_mapping["processing"])
            df_modelling = DataFrame(activity_mapping["modelling"])
            df_optimising = DataFrame(activity_mapping["optimising"])
            df_exporting = DataFrame(activity_mapping["exporting"])

            # Uploading the dataframes to relational database.
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

    def getById(self, id: str) -> DataFrame:
        endpoint =  self.getDbPathOrUrl()
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <https://schema.org/>
        SELECT ?name ?id ?type ?authorName ?authorId ?date ?owner ?place 
        WHERE {{
            ?entityId schema:identifier "{id}".
            ?entityId schema:name ?name.
          	?entityId schema:identifier ?id.
         	OPTIONAL {{
         	          ?entityId rdf:type ?typeId.
          	          ?typeId schema:name ?type.
                      ?entityId schema:author ?author.
                      ?author schema:name ?authorName.
                      ?author schema:identifier ?authorId.
                      ?entityId schema:dateCreated ?date.
                      ?entityId schema:location ?placeId.
                      ?placeId schema:name ?place.
                      ?entityId schema:owns ?ownerId.
                      ?ownerId schema:name ?owner.}}

        }}
        """
        try:
            df_id = get(endpoint, query, True).astype(str)

        except:
            df_id = DataFrame()

        return df_id

class MetadataQueryHandler(QueryHandler):

    def getAllPeople(self) -> DataFrame:

        endpoint = self.getDbPathOrUrl()
        query = """
               PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               PREFIX schema: <https://schema.org/>
               SELECT ?authorId ?name ?id 
               WHERE {
                    ?authorId rdf:type schema:Person.
                 	?authorId schema:name ?name.
                 	?authorId schema:identifier ?id.
               }
               """
        df_persons = get(endpoint, query, True).astype({"id": str})
        return df_persons

    def getAllCulturalHeritageObjects(self) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX schema: <https://schema.org/>
                    PREFIX wikidata: <https://www.wikidata.org/wiki/>
                    SELECT ?s ?id ?objectName ?type ?authorName ?authorId ?date ?owner ?place
                    WHERE {
                      VALUES ?typeId {
                        wikidata:Q728502
                        schema:Book
                        wikidata:Q181916
                        wikidata:Q1261026
                        wikidata:Q85869058
                        schema:Painting
                        schema:Map
                        schema:ArchiveComponent
                        schema:Manuscript
                        wikidata:Q1979154
                      }   
                      ?s rdf:type ?typeId.
                      ?typeId schema:name ?type.
                      ?s schema:identifier ?id.
                      ?s schema:name ?objectName.
                      ?s schema:author ?author.
                      ?author schema:name ?authorName.
                      ?author schema:identifier ?authorId.
                      ?s schema:dateCreated ?date.
                      ?s schema:owns ?ownerId.
                      ?ownerId schema:name ?owner.
                      ?s schema:location ?placeId.
                      ?placeId schema:name ?place.
                    }

                       """
        df_allCHObjects = get(endpoint, query, True).astype({"id": str, "date": str}).sort_values(by=["id"])
        return df_allCHObjects

    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> DataFrame:
        endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f'''
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>              
                SELECT ?author ?id
                WHERE {{
                       ?s schema:identifier "{objectId}".
                       ?s schema:author ?authorId.
                       ?authorId schema:identifier ?id.
                       ?authorId schema:name ?author.
                }}
        '''
        df_authorOFCHObject = get(endpoint, query, True).astype({"id": str})

        return df_authorOFCHObject

    # Get the Objects from the author input
    def getCulturalHeritageObjectsAuthoredBy(self, personId: str) -> DataFrame:
        endpoint = endpoint = MetadataUploadHandler.getDbPathOrUrl(self)
        query = f'''
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>              
                SELECT ?objectId ?title ?type ?authorName ?authorId ?date ?owner ?place
                WHERE {{
                  ?object schema:author ?author.
                  ?author schema:identifier "{personId}".
                  ?object schema:identifier ?objectId.
                  ?object schema:name ?title.
                  ?object rdf:type ?typeId.
                  ?typeId schema:name ?type.
                  ?author schema:name ?authorName.
                  ?author schema:identifier ?authorId.
                  ?object schema:dateCreated ?date.
                  ?object schema:owns ?ownerId.
                  ?ownerId schema:name ?owner.
                  ?object schema:location ?placeId.
                  ?placeId schema:name ?place.
                  }}
               '''

        df_objectByAuthor = get(endpoint, query, True).astype({"objectId": str, "date": str})
        return df_objectByAuthor

class ProcessDataQueryHandler(QueryHandler):

    def getAllActivities(self) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = """
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, technique, tool
                    FROM Acquisition
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Exporting
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Modelling
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Optimising
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Processing;
                    
            """
            df_activities = read_sql(query, con).astype(str)

            df_activities.drop(
                df_activities[
                    ((df_activities["responsible_institute"] == "") & (df_activities["start_date"] == "")
                   &  (df_activities["responsible_person"] == ""))
                    ].index,
                inplace=True
            )

            df_activities.reset_index(drop=True, inplace=True)
        return df_activities

    def getActivitiesByResponsibleInstitution(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, technique, tool 
                    FROM Acquisition
                    WHERE responsible_institute LIKE '%{partialName}%'
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Exporting
                    WHERE responsible_institute LIKE '%{partialName}%'
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Modelling
                    WHERE responsible_institute LIKE '%{partialName}%'
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Optimising
                    WHERE responsible_institute LIKE '%{partialName}%'
                    
                    UNION
                    SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                    start_date, end_date, Null As technique, tool
                    FROM Processing
                    WHERE responsible_institute LIKE '%{partialName}%';
            """
            df_activityByInstitute = read_sql(query, con).astype(str)

            df_activityByInstitute.drop(
                df_activityByInstitute[
                    ((df_activityByInstitute["responsible_institute"] == "")
                     & (df_activityByInstitute["start_date"] == "")
                     & (df_activityByInstitute["responsible_person"] == ""))].index,
                inplace=True
            )

            df_activityByInstitute.reset_index(drop=True, inplace=True)

        return df_activityByInstitute

    def getActivitiesByResponsiblePerson(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, technique, tool 
                               FROM Acquisition
                               WHERE responsible_person LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Exporting
                               WHERE responsible_person LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Modelling
                               WHERE responsible_person LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Optimising
                               WHERE responsible_person LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Processing
                               WHERE responsible_person LIKE '%{partialName}%';
                       """
            df_activityByPerson = read_sql(query, con).astype(str)

            df_activityByPerson.drop(
                df_activityByPerson[
                    ((df_activityByPerson["responsible_institute"] == "")
                     & (df_activityByPerson["start_date"] == "")
                     & (df_activityByPerson["responsible_person"] == ""))].index,
                inplace=True
            )

            df_activityByPerson.reset_index(drop=True, inplace=True)

        return df_activityByPerson

    def getActivitiesUsingTool(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, technique, tool 
                               FROM Acquisition
                               WHERE tool LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Exporting
                               WHERE tool LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Modelling
                               WHERE tool LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Optimising
                               WHERE tool LIKE '%{partialName}%'

                               UNION
                               SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                               start_date, end_date, Null As technique, tool
                               FROM Processing
                               WHERE tool LIKE '%{partialName}%';
                       """
            df_activityByTool = read_sql(query, con)

            df_activityByTool.drop(
                df_activityByTool[
                    ((df_activityByTool["responsible_institute"] == "")
                     & (df_activityByTool["start_date"] == "")
                     & (df_activityByTool["responsible_person"] == ""))].index,inplace=True
            )

            df_activityByTool.reset_index(drop=True, inplace=True)

        return df_activityByTool

    def getActivitiesStartedAfter(self, date: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, technique, tool 
                                FROM Acquisition
                                WHERE start_date > date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Exporting
                                WHERE start_date > date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Modelling
                                WHERE start_date > date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Optimising
                                WHERE start_date > date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Processing
                                WHERE start_date > date('{date}');
                        """
            df_activityBySD = read_sql(query, con)

        df_activityBySD.drop(
            df_activityBySD[
                ((df_activityBySD["responsible_institute"] == "")
                 & (df_activityBySD["start_date"] == "")
                 & (df_activityBySD["responsible_person"] == ""))].index, inplace=True
        )

        df_activityBySD.reset_index(drop=True, inplace=True)

        return df_activityBySD

    def getActivitiesEndedBefore(self, date: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, technique, tool 
                                FROM Acquisition
                                WHERE end_date < date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Exporting
                                WHERE end_date < date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Modelling
                                WHERE end_date < date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Optimising
                                WHERE end_date < date('{date}')

                                UNION
                                SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, Null As technique, tool
                                FROM Processing
                                WHERE end_date < date('{date}');
                        """
            df_activityByED = read_sql(query, con)

            # Drop the rows that there is No responsible institute. Because No activity is done in the latter row
            df_activityByED.drop(
                df_activityByED[
                    ((df_activityByED["responsible_institute"] == "")
                     & (df_activityByED["start_date"] == "")
                     & (df_activityByED["responsible_person"] == ""))].index, inplace=True
            )

            df_activityByED.reset_index(drop=True, inplace=True)

        return df_activityByED

    def getAcquisitionsByTechnique(self, partialName: str) -> DataFrame:
        with connect(ProcessDataUploadHandler.getDbPathOrUrl(self)) as con:
            query = f"""
                     SELECT activity_id, type, object_id, responsible_person, responsible_institute,
                                start_date, end_date, technique, tool 
                                FROM Acquisition WHERE technique LIKE '%{partialName}%'
            """
            df_acquisitionByTech = read_sql(query, con)

            df_acquisitionByTech.drop(
                df_acquisitionByTech[
                    ((df_acquisitionByTech["responsible_institute"] == "")
                     & (df_acquisitionByTech["start_date"] == "")
                     & (df_acquisitionByTech["responsible_person"] == ""))].index, inplace=True
            )

            df_acquisitionByTech.reset_index(drop=True, inplace=True)

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
            "optimising": Optimising,
            "processing": Processing
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
            df_ch_objects = metadata_handler.getById(id)

            # Group by id and ... and  make a list of author's data in the corresponding column
            match = df_ch_objects.groupby(["id", "type", "name", "date", "owner", "place"]).agg({
                'authorName' : lambda x: list(x.unique()), # Take only the unique values of authors
                'authorId' : lambda  x: list(x.unique())
            }).reset_index()
            if not match.empty:
                row = match.iloc[0]

             # Dynamically construct the object based on the type
                entity_class = self.type_to_class.get(row["type"])
                if entity_class:
                    return entity_class(id = row["id"],
                                        title = row["name"],
                                        author={"authorId": row["authorId"],
                                         "authorName": row["authorName"]},
                                        date=row["date"],
                                        owner=row["owner"],
                                        place=row["place"])

            # Query for person
            df_people = metadata_handler.getById(id)
            match = df_people[df_people["id"] == id]
            if not match.empty:
                row = match.iloc[0]
                return Person(id = row["id"], name = row["name"])

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
                person = Person(id = row["id"], name = row["name"])
                allPeople.append(person)

        return allPeople

    def getAllCulturalHeritageObjects(self) -> list[CulturalHeritageObject]:
        allCHObjects = []

        # Next is just like the previous method. except for the get method from the MetaDataQueryHandler class
        for metadata_handler in self.metadataQuery:
            df_CHObjects = metadata_handler.getAllCulturalHeritageObjects()

            df_CHObjects = df_CHObjects.groupby(["id", "objectName", "type", "date", "owner", "place"]).agg({
                'authorName' : lambda x: list(x.unique()),
                'authorId' : lambda  x: list(x.unique()),
            }).reset_index()

            for _, row in df_CHObjects.iterrows():
                # Dynamically construct the object based on the type
                entity_class = self.type_to_class.get(row["type"])

                if entity_class:
                    allCHObjects.append(entity_class(id = row["id"],
                                                     title = row["objectName"],
                                                     author = {"authorId": row["authorId"],
                                                             "authorName": row["authorName"]},
                                                     date = ["date"],
                                                     owner = ["owner"],
                                                     place = ["place"]))

        return allCHObjects

    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> list[Person]:
        allAuthors = []

        for metadata_handler in self.metadataQuery:
            df_authors = metadata_handler.getAuthorsOfCulturalHeritageObject(objectId)

            for _, row in df_authors.iterrows():
                author = Person(id = row["id"], name = row["author"])
                allAuthors.append(author)

        return allAuthors

    def getCulturalHeritageObjectsAuthoredBy(self, personId: str) -> list[CulturalHeritageObject]:
        CHObjects = []

        for metadata_handler in self.metadataQuery:
            df_CHObjects = metadata_handler.getCulturalHeritageObjectsAuthoredBy(personId)

            df_CHObjects = df_CHObjects.groupby(["objectId", "title", "type", "date", "owner", "place"]).agg({
                'authorName' : lambda x: list(x),
                'authorId' : lambda  x: list(x),
            }).reset_index()

            for _, row in df_CHObjects.iterrows():
                entity_class = self.type_to_class.get(row["type"])

                if entity_class:
                    CHObjects.append(entity_class(id = row["objectId"],
                                                  title = row["title"],
                                                author = {"authorId": row["authorId"],
                                                          "authorName": row["authorName"]},
                                                  date = row["date"],
                                                  owner = row["owner"],
                                                  place = row["place"]))

        return CHObjects

    def getAllActivities(self) -> list[Activity]:
        allActivities = []

        # Iterate through the list of Process Query objects (Like metadata query objects)
        for process_handler in self.processQuery:
            df_allActivities = process_handler.getAllActivities()

            for _, row in df_allActivities.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    allActivities.append(activity_class(technique = row["technique"],
                                                        institute = row["responsible_institute"],
                                                        person = row["responsible_person"],
                                                        tool = row["tool"].split("; "),
                                                        start = row["start_date"],
                                                        end = row["end_date"],
                                                        cultural_heritage_object = self.getEntityById(row["object_id"])
                                                        ))

                elif activity_class:
                    allActivities.append(activity_class(institute = row["responsible_institute"],
                                                        person = row["responsible_person"],
                                                        tool = row["tool"].split("; "),
                                                        start = row["start_date"],
                                                        end = row["end_date"],
                                                        cultural_heritage_object = self.getEntityById(row["object_id"])
                                                        ))

        return allActivities

    def getActivitiesByResponsibleInstitution(self, partialName: str) -> list[Activity]:
        activityByInst = []

        for process_handler in self.processQuery:
            df_activityByInst = process_handler.getActivitiesByResponsibleInstitution(partialName)

            for _, row in df_activityByInst.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    activityByInst.append(activity_class(technique = row["technique"],
                                                         institute = row["responsible_institute"],
                                                         person = ["responsible_person"],
                                                         tool = row["tool"].split("; "),
                                                         start = row["start_date"],
                                                         end = row["end_date"],
                                                         cultural_heritage_object = self.getEntityById(row["object_id"])
                                                         ))
                elif activity_class:
                    activityByInst.append(activity_class(institute = row["responsible_institute"],
                                                        person = row["responsible_person"],
                                                        tool = row["tool"].split("; "),
                                                        start = row["start_date"],
                                                        end = row["end_date"],
                                                        cultural_heritage_object = self.getEntityById(row["object_id"])
                                                        ))

        return activityByInst

    def getActivitiesByResponsiblePerson(self, partialName: str) -> list[Activity]:
        activityByPers = []

        for process_handler in self.processQuery:
            df_activityByPers = process_handler.getActivitiesByResponsiblePerson(partialName)

            for _, row in df_activityByPers.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    activityByPers.append(activity_class(technique = row["technique"],
                                                         institute = row["responsible_institute"],
                                                         person = row["responsible_person"],
                                                         tool = row["tool"].split("; "),
                                                         start = row["start_date"],
                                                         end = row["end_date"],
                                                         cultural_heritage_object = self.getEntityById(row["object_id"])
                                                         ))
                elif activity_class:
                    activityByPers.append(activity_class(institute = row["responsible_institute"],
                                                        person = row["responsible_person"],
                                                        tool = row["tool"].split("; "),
                                                        start = row["start_date"],
                                                        end = row["end_date"],
                                                        cultural_heritage_object = self.getEntityById(row["object_id"])
                                                        ))

        return activityByPers

    def getActivitiesUsingTool(self, partialName: str) -> list[Activity]:
        activityUsingTool = []

        for process_handler in self.processQuery:
            df_activityUsingTool = process_handler.getActivitiesUsingTool(partialName)

            for _, row in df_activityUsingTool.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    activityUsingTool.append(activity_class(technique = row["technique"],
                                                         institute = row["responsible_institute"],
                                                         person = row["responsible_person"],
                                                         tool = row["tool"].split("; "),
                                                         start = row["start_date"],
                                                         end = row["end_date"],
                                                         cultural_heritage_object = self.getEntityById(row["object_id"])
                                                         ))
                elif activity_class:
                    activityUsingTool.append(activity_class(institute = row["responsible_institute"],
                                                        person = row["responsible_person"],
                                                        tool = row["tool"].split("; "),
                                                        start = row["start_date"],
                                                        end = row["end_date"],
                                                        cultural_heritage_object = self.getEntityById(row["object_id"])
                                                        ))

        return activityUsingTool

    def getActivitiesStartedAfter(self, date: str) -> list[Activity]:
        activityStartedAfter = []

        for processHandler in self.processQuery:
            df_activityStartedAfter = processHandler.getActivitiesStartedAfter(date)

            for _, row in df_activityStartedAfter.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    activityStartedAfter.append(activity_class(technique = row["technique"],
                                                         institute = row["responsible_institute"],
                                                         person = row["responsible_person"],
                                                         tool = row["tool"].split("; "),
                                                         start = row["start_date"],
                                                         end = row["end_date"],
                                                         cultural_heritage_object = self.getEntityById(row["object_id"])
                                                         ))
                elif activity_class:
                    activityStartedAfter.append(activity_class(institute = row["responsible_institute"],
                                                        person = row["responsible_person"],
                                                        tool = row["tool"].split("; "),
                                                        start = row["start_date"],
                                                        end = row["end_date"],
                                                        cultural_heritage_object = self.getEntityById(row["object_id"])
                                                        ))
        return activityStartedAfter

    def getActivitiesEndedBefore(self, date: str) -> list[Activity]:
        activityEndedBefore = []

        for processHandler in self.processQuery:
            df_activityEndedBefore = processHandler.getActivitiesEndedBefore(date)

            for _, row in df_activityEndedBefore.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    activityEndedBefore.append(activity_class(technique = row["technique"],
                                                               institute = row["responsible_institute"],
                                                               person = row["responsible_person"],
                                                               tool = row["tool"].split("; "),
                                                               start = row["start_date"],
                                                               end = row["end_date"],
                                                               cultural_heritage_object = self.getEntityById(row["object_id"])
                                                               ))
                elif activity_class:
                    activityEndedBefore.append(activity_class(institute = row["responsible_institute"],
                                                               person = row["responsible_person"],
                                                               tool = row["tool"].split("; "),
                                                               start = row["start_date"],
                                                               end = row["end_date"],
                                                               cultural_heritage_object = self.getEntityById(row["object_id"])
                                                               ))
        return activityEndedBefore

    def getAcquisitionsByTechnique(self, partialName: str) -> list[Acquisition]:
        acquisitionByTech = []

        for processHandler in self.processQuery:
            df_acquisitionByTech = processHandler.getAcquisitionsByTechnique(partialName)

            for _, row in df_acquisitionByTech.iterrows():
                activity_class = self.activity_to_class.get(row["type"])

                if activity_class and activity_class == Acquisition:
                    acquisitionByTech.append(activity_class(technique = row["technique"],
                                                               institute = row["responsible_institute"],
                                                               person = row["responsible_person"],
                                                               tool = row["tool"].split("; "),
                                                               start = row["start_date"],
                                                               end = row["end_date"],
                                                               cultural_heritage_object = self.getEntityById(row["object_id"])
                                                               ))

        return acquisitionByTech

class AdvancedMashup(BasicMashup):

    def getActivitiesOnObjectsAuthoredBy(self, personId: str) -> list[Activity]:

        ActivitiesByAuthor = []
        CHObjects = self.getCulturalHeritageObjectsAuthoredBy(personId)
        CHObjectsIds = [Object.getId() for Object in CHObjects] # Build a list of Ids of CHObjects done by Author
        AllActivities = self.getAllActivities()

        for activity in AllActivities: # Iterate through all the activities
            ObjectIdReferred = activity.refersTo().getId() # Get the Object referred and Get its Id
            if ObjectIdReferred in CHObjectsIds: # Check if te id of referred Object is in the object Ids by the Author
                ActivitiesByAuthor.append(activity)

        return ActivitiesByAuthor

    def getObjectsHandledByResponsiblePerson(self, partialName: str) -> list[CulturalHeritageObject]:

        # Keeping the ids got from refers to in a set to remove duplicates
        ObjectIds = set()
        activitiesByResPers = self.getActivitiesByResponsiblePerson(partialName)

        if activitiesByResPers:
            for activity in activitiesByResPers:

                ObjectByActivity = activity.refersTo() # Get the Cultural Heritage Objects from activities

                Object_Id = ObjectByActivity.getId() #Get the Object id
                if Object_Id not in ObjectIds:
                    ObjectIds.add(Object_Id) # Add it to the set to filter out duplicates

        ObjectsByResPers = [self.getEntityById(i) for i in ObjectIds] # The list of Objects given the ids

        return ObjectsByResPers

    def getObjectsHandledByResponsibleInstitution(self, partialName: str) -> list[CulturalHeritageObject]:

        # The procedure is the same as previous class
        ObjectIds = set()
        activitiesByResInst = self.getActivitiesByResponsibleInstitution(partialName)

        if activitiesByResInst:
            for activity in activitiesByResInst:

                ObjectByActivity = activity.refersTo()

                Object_Id = ObjectByActivity.getId()
                if Object_Id not in ObjectIds:
                    ObjectIds.add(Object_Id)

        ObjectsByResInst = [self.getEntityById(i) for i in ObjectIds] # The list of Objects given the ids

        return ObjectsByResInst

    def getAuthorsOfObjectsAcquiredInTimeFrame(self, start: str, end: str) -> list[Person]:

        AuthorIds = set()

        allActivities = self.getAllActivities()  # Getting all the activities

        for activity in allActivities:
                                               # Filter the Acquisition activity
            if hasattr(activity, "technique"): # Because only the acquisition activity has the attribute technique
                    # Check if the start and end date of the acquisition is between the given dates
                if activity.getStartDate() > start and activity.getEndDate() < end:
                    CHObject = activity.refersTo()
                    ObjectId = CHObject.getId()

                    author = self.getAuthorsOfCulturalHeritageObject(ObjectId)
                    if author and len(author)>0:
                        for i in author:
                            AuthorIds.add(i.getId())


        Authors = [self.getEntityById(i) for i in AuthorIds]

        return Authors