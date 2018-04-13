import os
import logging

from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUBSCRIPTIONS = os.getenv("subscription_list", ["54dd3907-ccd0-4338-963e-6a58a10266f2"])
SECRET = os.getenv("AZURE_SECRET")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")


def list_resource_groups(subscription_id):
    
    creds = get_service_principal_cred()
    client = ResourceManagementClient(credentials=creds, subscription_id=subscription_id)
    res = client.resource_groups.list()

    resource_group_list = []
    for rg in res:
        _ = rg.as_dict()
        resource_group_list.append(_)

    return resource_group_list

def get_service_principal_cred():
    logger.debug("Retrieving a ServicePrincipal credential")

    creds = ServicePrincipalCredentials(
        client_id = os.getenv('AZURE_CLIENT_ID'),
        secret=SECRET,
        tenant=os.getenv('AZURE_TENANT_ID')
    )

    return creds

def main():
    for id in SUBSCRIPTIONS:
        logging.debug("Current Subscription set to {0}".format(id))

        res = list_resource_groups(subscription_id=id)
        for rg in res:
            print(rg)

main()




