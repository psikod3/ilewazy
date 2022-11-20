import pickle
import pandas as pd
import pymongo

ilewazy = pd.read_pickle('ilewazy.pkl')
# ilewazy.reset_index(inplace=True)


def create_MongoDB(new_data: pd.DataFrame, collection: pymongo.collection.Collection) -> None:
    """Creates MongoDB database by inserting pandas DataFrame into it."""
    for row in new_data.to_dict('records'):
        collection.insert_one(row)
        print('robiem')
    print("Finished creating MongoDB.")

def connection_to_mongodb(host: str, port: str, db_name: str, collection_name: str) -> pymongo.collection.Collection:
    """Creates connection with Collection from MongoDB."""
    client = pymongo.MongoClient(f"mongodb://{host}:{port}")
    db = client[db_name]
    offers_collection = db[collection_name]
    return offers_collection

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['db_ilewazy']
offers_collection = db['Produkty']
create_MongoDB(ilewazy, offers_collection)

# company = db['Test']
# ilewazy.reset_index(inplace=True)
# data_dict = ilewazy.to_dict("records")
# company.insert_one({"index":"Sensex","data":data_dict})

print(ilewazy.head())
