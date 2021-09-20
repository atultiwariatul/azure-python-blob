from azure.storage.blob import BlobClient
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from services.AzureBlobAdapter import AzureBlobAdapter
app_api = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
app_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app_api.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
blob_client: BlobClient

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


def save_file_to_local_folder():
    file_paths = {}
    files = request.files.getlist("files[]")
    for file in files:
        local_file_name = "IN_CARE_" + str(uuid.uuid4()) + file.filename
        full_path_to_file = os.path.join(
            app_api.config['UPLOAD_FOLDER'], local_file_name)
        print(" Full path to file {}".format(full_path_to_file))
        filename = secure_filename(local_file_name)
        file.save(os.path.join(app_api.config['UPLOAD_FOLDER'], filename))
        file.close()
        file_paths[filename] = full_path_to_file
    return file_paths


@app_api.route('/python-flask-files-upload', methods=['POST'])
def upload_fileee():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')

    errors = {}
    success = False

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            files_dict = save_file_to_local_folder()
            print('Files Dict:')
            print(files_dict)
            status = AzureBlobAdapter().upload(files_dict)
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp

def download_file():
    args = request.args
    print(args)  # For debugging
    file_name = args['file_name']
    print("Downloading file....")
    save_blob_to_download_folder(file_name)
    return "Downloaded to downloads folder."


@app_api.route("/list", methods=["GET"])
def list_files():
    #     print("listing files...")
    #     # blobs = AzureBlobAdapter().list_blobs()
    #     # return jsonify(blobs)
    container = AzureBlobAdapter().getConfig('container_name')
    return render_template('blob_list.html', container=container)


@app_api.route("/api/data", methods=["GET"])
def data():
    return {'data': convert(AzureBlobAdapter().list_blobs())}


def convert(a):
    data_arr = []
    for blob_name in a:
        blob_dict = {'name': blob_name}
        # print('Blob name in convert:'+blob_name)
        data_arr.append(blob_dict)
    return data_arr


def save_blob_to_download_folder(file_name):
    blob_client = AzureBlobAdapter().get_blob_client(file_name)
    download_file_path = os.path.join('downloads', file_name)
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(download_file_path, "wb") as download_file_local:
        download_file_local.write(blob_client.download_blob().readall())
    return True


def prepare_upload_dir():
    if not os.path.exists('uploads'):
        os.makedirs(os.path(UPLOAD_FOLDER))


class CustomBlob():
    def __init__(self):
        pass

    name = ''

    def to_dict(self):
        return {
            'name': self.name,
        }
