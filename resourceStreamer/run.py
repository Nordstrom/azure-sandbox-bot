import os
import logging
import sys
import json

# update path to point to azure's app fabric to use venv for dependent modules.
# - use the console tool
# -  python -m pip -U pip
# - python -m virtualenv venv
# - venv/Scripts/activate.bat
# - python -m pip install -r requirements.txt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../venv/Lib/site-packages')))
import requests
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# list of sandbox subscriptions
SUBSCRIPTIONS = os.getenv("subscription_list", ["54dd3907-ccd0-4338-963e-6a58a10266f2"])

# vars related to service principal which is the identity we use for azure cmds
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
SP_SECRET_URI = os.getenv("SP_SECRET_URI")
AZURE_FUNCTION_OUTPUT_QUEUE = "myQueueItem"

def list_resource_groups(subscription_id):
    creds = get_service_principal_cred()
    client = ResourceManagementClient(credentials=creds, subscription_id=subscription_id)
    res = client.resource_groups.list()

    resource_group_list = []
    for rg in res:
        _ = rg.as_dict()
        resource_group_list.append(_)

    return resource_group_list


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

def send_to_queue(body):

    return_dict = {
        "body": body,
        "headers": {
            "Content-Type": "application/json"
        }
    }
    output = open(os.environ[AZURE_FUNCTION_OUTPUT_QUEUE], 'w')
    output.write(json.dumps(return_dict))


def main():
    print("starting...")

    resources_list = []
    for id in SUBSCRIPTIONS:
        logging.debug("Current Subscription set to {0}".format(id))

        resourceGroups = []
        res = list_resource_groups(subscription_id=id)
        for rg in res:
            resourceGroups.append({"resource_id": rg["name"],
                                   "subscription": id})
        
        resources_list.append({id:resourceGroups})

    resource_dict = {"resources": resources_list}
    send_to_queue(resource_dict)

main()