from google.cloud import datastore
from config import DATASTORE_PROJECT_ID

client = datastore.Client()

def get_user(user_id):
    key = client.key('User', user_id)
    return client.get(key)

