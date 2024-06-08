# CLIENT_ID = 'M7E3nhzw81aI6hpzd3OgOqU5C3MA1vti'
# CLIENT_SECRET = '1dDYBFH0BJ0f1IpA_nLjbwuaar_nXG2GX4FfhiKlcUxkP3189HkTYii70vtkxt3v'
# DOMAIN = 'dev-jwt-493spring24.us.auth0.com'

# DATASTORE_PROJECT_ID = 'tarpaulincms-api'
# CLOUD_BUCKET = 'bucket-today-1'

import os
from dotenv import load_dotenv

# Load environment variables from .env file if running locally
if os.getenv('FLASK_ENV') != 'production':
    load_dotenv()

def get_env_variable(var_name):
    """ Get the environment variable or raise an exception. """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Set the {var_name} environment variable."
        raise EnvironmentError(error_msg)

def access_secret_version(project_id, secret_id, version_id='latest'):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

# Check if running in production environment
if os.getenv('FLASK_ENV') == 'production':
    project_id = get_env_variable('GOOGLE_CLOUD_PROJECT')
    CLIENT_ID = access_secret_version(project_id, 'CLIENT_ID')
    CLIENT_SECRET = access_secret_version(project_id, 'CLIENT_SECRET')
    DOMAIN = access_secret_version(project_id, 'DOMAIN')
    DATASTORE_PROJECT_ID = access_secret_version(project_id, 'DATASTORE_PROJECT_ID')
    CLOUD_BUCKET = access_secret_version(project_id, 'CLOUD_BUCKET')
else:
    CLIENT_ID = get_env_variable('CLIENT_ID')
    CLIENT_SECRET = get_env_variable('CLIENT_SECRET')
    DOMAIN = get_env_variable('DOMAIN')
    DATASTORE_PROJECT_ID = get_env_variable('DATASTORE_PROJECT_ID')
    CLOUD_BUCKET = get_env_variable('CLOUD_BUCKET')

