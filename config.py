from dotenv import load_dotenv
from dotenv import dotenv_values


load_dotenv()
values_env = dotenv_values(".env")

MODEL_NAME=values_env["MODEL_NAME"]
MODEL_NAME_CLIP=values_env["MODEL_NAME_CLIP"]
IMAGES_PATH =values_env["IMAGES_PATH"]

# Qdrant server URL
URL =values_env["URL"]
# Qdrant dimension of the collection
DIMENSION = values_env["DIMENSION"]
# Qdrant collection name
COLLECTION_NAME = values_env["COLLECTION_NAME"]
METRIC_NAME =values_env["METRIC_NAME"]

KEY = values_env["KEY"]
ENDPOINT = values_env["ENDPOINT"]
LOCATION = values_env["LOCATION"]
DEPLOYMENT_ID = values_env["DEPLOYMENT_ID"]