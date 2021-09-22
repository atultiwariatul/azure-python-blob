import configparser
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from flask import jsonify

class AzureBlobAdapter:
    FILE_PREFIX = 'IN_CARE'
    blob_service_client: BlobServiceClient
    blob_client: BlobClient
    container_client: ContainerClient
    configs = configparser.ConfigParser()
    configs.read('azure_blob.cfg')

    # init method or constructor

    def __init__(self):
        connection_string = self.get_config('connection_string')
        print("Azure Blob Storage v" + __version__ +
              " - Blob Python libs")
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string)

    def upload(self, file_dict):
        upload_response = {}
        for key in file_dict:
            print("File Dict Key: [{}] value is: {}".format(key, file_dict[key]))
            print("\nUploading to Azure Storage as blob:\n\t" + key)

            self.blob_client = self.blob_service_client.get_blob_client(container=self.get_config('container_name'), blob=key)
            with open(file_dict[key], "rb") as data:
                try:
                    self.blob_client.upload_blob(data)
                    print('File: Uploaded Successfully: {}'.format(key))
                    upload_response[key] = 'Successfully Uploaded'
                except ResourceExistsError:
                    print('File: NOT Uploaded Successfully: {}'.format(key))
                    upload_response[key] = 'This Resource already exists'
                    upload_response['Partial'] = True
                    print('This Resource already exists')
                    # return 'This Resource already exists'
        print("Before Returning Response:")
        print(jsonify(upload_response))
        print("---------------")
        return upload_response

    def get_blob_client(self, blob_name):
        self.blob_client = self.blob_service_client.get_blob_client(
            container=self.get_config('container_name'), blob=blob_name)
        return self.blob_client

    def list_blobs(self):
        print("\nList blobs in the container")
        self.container_client = self.blob_service_client.get_container_client(
            container=self.get_config('container_name'))
        blob_list = self.container_client.list_blobs()
        blobs = []
        for blob in blob_list:
            # print("\t Blob name: " + blob.name)
            blobs.append(blob.name)
        return blobs

    def get_config(self, app_property):
        config_value = self.configs['azure_blob_config'][app_property]
        return config_value
