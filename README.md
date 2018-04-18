# azure-sandbox-bot
Set of Azure functions for maintaining Sandbox subscriptions

## SUMMARY

This is an Azure Function App that collects and removes resources deployed with in the Azure Sandbox subscriptions and a set time interval.

The solution is a set of serverless functions combined with a storage queue to collect and delete.  The solution is written in python 3.6 utilizing the Azure python SDK.

https://docs.microsoft.com/en-us/python/azure/?view=azure-python


## DEPLOYMENT

The solution utilizes a CICD pipeline on top of a Nordstrom org GitHub repo.  A push to the "dev" repo will kick of a deployment to the NonProd IEPC subscription.

### Authentication
This solution utilizes a collection of resources to allow the functions to allow for authentication.  

#### Service Principal
https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-application-objects

A service principal has been created that allows for the solution to operate against the sandbox subscriptions.  This SP is scoped only to the sandbox subscription. 

Azure Key Vault is used to store the SP secret.  This allows for a centralized and protected means of providing a management credential for a set of use cases. 
https://docs.microsoft.com/en-us/azure/key-vault/key-vault-whatis

Mananaged Service Identity.
https://docs.microsoft.com/en-us/azure/active-directory/managed-service-identity/overview
