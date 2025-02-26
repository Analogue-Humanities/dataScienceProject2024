
# Data Science Project

## The final project of the Data Science Course 2024 at the University of Bologna

This Project is implemented in Python Programming Language and is object orented by defining python classes for all the functionalities of the program.
It aims at reading two source files as input, Preprocess them and cleanse the data, make two databases; One relational and the other graph database. Then upload the data to the databases.
Then the program provides some methods in different classes.

The project description can be found on [the course github page](https://github.com/comp-data/2023-2024/tree/main/docs/project).
The UML shows the different parts of the software. It is provided by the course instructor. 

## The relational database

For the relational database sqlite is used for the simplicity and the size of the project. Then in the QueryHandler classes the relational database is queried by sql language and returns pandas dataframes in resonse which is used 
in mashup class methods. 

## The graph database

The Graph database is created by RDF triples (subject, predicate, object). It uploads the graph to blazegraph, which is Database management system for graph database. Sparql is also used to query the graph database. To query the database in python
*sparql_dataframe* library is used.

## Running the project

In order to run the project, first you should run the blazegraph server locally. Download the .jar file of the Blazegraph from [here] (https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_2_1_6_RC/blazegraph.jar) and run it
in your directory using

    java -server -Xmx1g -jar blazegraph.jar

Before Running the project please ensure that all the requirements of the project is installed properly. you can install them using 

    pip install -r requirements.txt

You can run the [running_code.py](running_code.py) to have an idea how it works. The provided examplary input files are a [json file](data/meta.json) and [csv file](data/meta.csv). You can use your own files until you stick to the project specifications.
The mandatory specifications are the name and number of columns, the keys in the jason file, and providing id and title for the records.

If you want to use it on other types instead of the the types provided in this file, you should change the class CulturalHeritageObject(IdentifiableEntity) part in source code file [impl.py](impl.py).

## Note on AdvancedMashup class

This class is implemented using the already existing methods in the BasicMashup class.
Another way to implement it was Joining the dataframes from both databases created in the Query classes. I will develop this implementation in the future to compare the results.


