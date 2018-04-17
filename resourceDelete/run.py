import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../venv/Lib/site-packages')))
import requests
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials

SP_SECRET_URI = os.getenv("SP_SECRET_URI")

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_kv_api_token():
    MSI_ENDPOINT = os.getenv("MSI_ENDPOINT")
    MSI_SECRET = os.getenv("MSI_SECRET")

    RESOURCE_URI = "https://vault.azure.net"
    TOKEN_AUTH_URI = "{0}?resource={1}&api-version=2017-09-01".format(MSI_ENDPOINT, RESOURCE_URI)

    headers = {"Secret": MSI_SECRET}

    res = requests.get(TOKEN_AUTH_URI, headers=headers)
    jres = res.json()
    return jres["access_token"]


def get_sp_secret():
    token = get_kv_api_token()
    SECRET_URI = "{0}?api-version=2016-10-01".format(SP_SECRET_URI)

    headers = {"Authorization": "Bearer {0}".format(token)}
    res = requests.get(SECRET_URI, headers=headers)
    jres = res.json()
    return jres["value"]


def get_service_principal_cred():
    logger.debug("Retrieving a ServicePrincipal credential")

    creds = ServicePrincipalCredentials(
        client_id=os.getenv('AZURE_CLIENT_ID'),
        secret=get_sp_secret(),
        tenant=os.getenv('AZURE_TENANT_ID')
    )
    return creds

def process_queue_item(msg, client):
    delete_resource_group(subscription=msg, rg='', client=client)
    

def delete_resource_group(subscription, rg, client):

    client.resource_groups.delete()


def main():

    msg = open(os.environ['myQueueItem']).read()
    resource_list = msg["body"]["resources"]
    
    for sub in resource_list:

        creds = get_service_principal_cred()
        client = ResourceManagementClient(credentials=creds, subscription_id=sub)
        
        subscription_id = sub.keys()[0]
        for resource_item in sub[subscription_id]:
            print("Would delete {0}".format(resource_item))

main()
