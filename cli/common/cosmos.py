import os

from azure.cosmos import CosmosClient

settings = {
    'host': os.environ.get('ACCOUNT_HOST'),
    'master_key': os.environ.get('ACCOUNT_KEY'),
    'database_id': os.environ.get('COSMOS_DATABASE'),
    'container_id': os.environ.get('COSMOS_CONTAINER'),
}


URL = os.environ['COSMOS_ACCOUNT_URI']
KEY = os.environ['COSMOS_ACCOUNT_KEY']
DATABASE_NAME = os.environ['DATABASE_NAME']

client = CosmosClient(URL, credential=KEY)
database = client.get_database_client(DATABASE_NAME)

