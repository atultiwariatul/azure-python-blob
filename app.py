import os
import sys
from azure.storage.blob import BlobClient
from flask import Flask, render_template, request, jsonify, make_response, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

sys.path.append(os.getcwd())
from login_app import login_api
import app_config
from services.AzureBlobAdapter import AzureBlobAdapter

# from create_app import create_app

app = Flask(__name__)
app.config.from_object(app_config)
app.register_blueprint(login_api)
Session(app)
UPLOAD_FOLDER = '/tmp/uploads'
DOWNLOAD_FOLDER = '/tmp/downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
blob_client: BlobClient
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file_to_local_folder():
    prepare_upload_dir()
    file_paths = {}
    files = request.files.getlist("files[]")
    for file in files:
        # local_file_name = "IN_CARE_" + str(uuid.uuid4()) + file.filename
        full_path_to_file = os.path.join(
            app.config['UPLOAD_FOLDER'], file.filename)
        print(" Full path to file {}".format(full_path_to_file))
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # file.close()
        file_paths[filename] = full_path_to_file
    return file_paths


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/file-upload', methods=['POST'])
def upload_file():
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
            azure_response = AzureBlobAdapter().upload(files_dict)
            print('Response:=> {}'.format(jsonify(azure_response)))
            if azure_response != 'Success':
                print('Reporting error to frontend')
                errors[file.filename] = azure_response
            else:
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
        print('Coming in Else part: Returning Errors:')
        return make_response(errors, 400)


@app.route('/download', methods=['GET'])
def download_file():
    print("Download files....")
    args = request.args
    print(args)  # For debugging
    file_name = args['file_name']
    print("Downloading file....")
    save_blob_to_download_folder(file_name)
    # Return stream data
    filename = save_blob_to_download_folder(file_name)
    return send_file(filename, mimetype='application/octetstream')


@app.route("/list", methods=["GET"])
def list_files():
    container = AzureBlobAdapter().get_config('container_name')
    return render_template('blob_list.html', container=container)


@app.route("/api/data", methods=["GET"])
def data():
    return {'data': convert(AzureBlobAdapter().list_blobs())}


def convert(a):
    data_arr = []
    download_link = "<a id=\"link\" onclick=\"DownloadFile('{}')\" href=\"#\">Download</a>"
    for blob_name in a:
        blob_dict = {'name': blob_name, 'download_url': download_link.format(blob_name)}
        # print('Blob name in convert:'+blob_name)
        data_arr.append(blob_dict)
    return data_arr


def save_blob_to_download_folder(file_name):
    blob_client = AzureBlobAdapter().get_blob_client(file_name)
    prepare_download_dir()
    download_file_path = os.path.join('/tmp/downloads', file_name)
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(download_file_path, "wb") as download_file_local:
        download_file_local.write(blob_client.download_blob().readall())
    return download_file_path


def prepare_upload_dir():
    print('Preparing upload folder.')
    if not os.path.exists(UPLOAD_FOLDER):
        print('upload folder doesnt exists .')
        os.makedirs(UPLOAD_FOLDER)
    else:
        print('Upload folder already exits.')


def prepare_download_dir():
    print('Preparing Download folder.')
    if not os.path.exists(DOWNLOAD_FOLDER):
        print('Download folder doesnt exists .')
        os.makedirs(DOWNLOAD_FOLDER)
    else:
        print('Download folder already exits.')

# app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template
# app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
