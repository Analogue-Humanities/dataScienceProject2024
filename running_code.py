from impl import Handler, MetadataUploadHandler, ProcessDataUploadHandler
import pandas as pd

hand = Handler()

print(hand.getDbPathOrUrl())

path1 = 'data/process.json'
hand.setDbPathOrUrl(path1)
file1 = hand.getDbPathOrUrl()
print(file1)

process = ProcessDataUploadHandler()

df = process.pushDataToDb(file1)
print(df)

#df.to_csv('test.csv')

path2 = 'data/meta.csv'
hand.setDbPathOrUrl(path2)
hand.getDbPathOrUrl()

meta = MetadataUploadHandler()

test = meta.pushDataToDb(hand.getDbPathOrUrl())
print(test)

#########################################################################################
# The way it is implemented in the project specifications

rel_path = "relational.db"
process = ProcessDataUploadHandler()
process.setDbPathOrUrl(rel_path)
process.pushDataToDb("data/process.json")