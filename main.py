import google.auth
from googleapiclient import discovery
import json 
import base64
from google.cloud import secretmanager


credentials, project = google.auth.default()
crm = discovery.build("cloudresourcemanager", "v3", credentials=credentials)
iam = discovery.build("iam", "v1", credentials=credentials)
sm = discovery.build("secretmanager", "v1", credentials = credentials)
#ecrets_client = secretmanager.SecretManagerServiceClient()

projects_list = crm.projects().search().execute()
#print(projects_list)

for r in projects_list['projects']:
    project_id = r['projectId']
    project_name = f'projects/{project_id}'
    service_account_list = iam.projects().serviceAccounts().list(name=project_name).execute()
    for q in service_account_list['accounts']: 
        name = q['name']
        secret_id = name.replace('@', '_').replace('.', '_')
        key_list = iam.projects().serviceAccounts().keys().list(name=name, keyTypes = "USER_MANAGED").execute()
        parent = f"projects/{project_id}"
        sec_name = name.split("@")[0].replace("/", "-")
        secret = sm.projects().secrets().create(parent = parent, secretId = sec_name, body = {"replication": {"automatic": {}}}).execute()
        secret_ref = secret['name']
        service_account_key  = iam.projects().serviceAccounts().keys().create(name = name, body={}).execute()
        key_data = (service_account_key['privateKeyData'])
        version = sm.projects().secrets().addVersion(parent = secret_ref, body =  {"payload": {"data": key_data}}).execute()
        