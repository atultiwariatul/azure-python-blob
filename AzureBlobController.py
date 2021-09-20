# https: // docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python
# https://docs.microsoft.com/en-us/azure/storage/files/storage-python-how-to-use-file-storage?tabs=python
# https://pypi.org/project/azure-storage-blob/
# https://towardsdatascience.com/working-with-apis-using-flask-flask-restplus-and-swagger-ui-7cf447deda7f
# https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
from azure.storage.blob import BlobClient
from flask import Blueprint, Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from services.AzureBlobAdapter import AzureBlobAdapter
# app_api = Flask(__name__)
app_api = Blueprint('app_api', __name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
# app_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
blob_client: BlobClient


@app_api.route('/uploader')
def uploader_html():
    return render_template('/upload.html')


@app_api.route("/upload", methods=["POST"])
def upload_file():
    print("Uploading file...")
    files_dict = save_file_to_local_folder()
    try:
        status = AzureBlobAdapter().upload(files_dict)
        if status == True:
            print('Upload successfull...')
            return "Upload Success"
        else:
            print('UPload Failed.')
            return "Failed..."
    except Exception as err:
        print("Oops! Try again...{}".format(err))


@app_api.route("/download", methods=["GET"])
def download_file():
    args = request.args
    print(args)  # For debugging
    file_name = args['file_name']
    print("Downloading file....")
    save_blob_to_download_folder(file_name)
    return "Downloaded to downloads folder."


# @app_api.route("/list", methods=["GET"])
# def list_files():
#     print("listing files...")
#     # blobs = AzureBlobAdapter().list_blobs()
#     # return jsonify(blobs)
#     return render_template('ajax_table.html', title='Ajax Table')

@app_api.route("/api", methods=["GET"])
def data():
    return {'data': AzureBlobAdapter().list_blobs()}


@app_api.route("/test", methods=["GET"])
def test():
    return "test";    


def save_blob_to_download_folder(file_name):
    blob_client = AzureBlobAdapter().get_blob_client(file_name)
    download_file_path = os.path.join('downloads', file_name)
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    return True


def save_file_to_local_folder():
    file_paths = {}
    files = request.files.getlist("file")
    prepare_upload_dir()
    for file in files:
        local_file_name = "IN_CARE_" + str(uuid.uuid4()) + file.filename
        full_path_to_file = os.path.join(
            'uploads', local_file_name)
        print(" Full path to file {}".format(full_path_to_file))
        filename = secure_filename(local_file_name)
        file.save(os.path.join('uploads', filename))
        file.close()
        file_paths[filename] = full_path_to_file

    return file_paths


def prepare_upload_dir():
    if not os.path.exists('uploads'):
        os.makedirs(os.path(UPLOAD_FOLDER))
