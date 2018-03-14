from __future__ import division

import requests
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, redirect, url_for
import cf_deployment_tracker
import os
from PIL import Image
import base64
from io import BytesIO
import json
import time

MAX_IMAGE_WIDTH = 1920
MAX_IMAGE_HEIGHT = 918
MAX_IMAGE_ID = 19

cf_deployment_tracker.track()

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
elif os.path.isfile('static/config/vcap-local.json'):
    with open('static/config/vcap-local.json') as f:
        vcap = json.load(f)
else:
    raise ValueError('No VCAP service available.')

creds = vcap['cloudantNoSQLDB'][0]['credentials']
username = creds['username']
password = creds['password']
database = 'guest-slides'
database_url = 'https://' + creds['host'] + '/' + database

port = int(os.getenv('PORT', 8080))


def get_cloudant_view(limit=1, skip=0, startkey=0):
    view_url = database_url + '/_design/main/_view/by-timestamp'
    args = {
        'skip':         skip,
        'startkey':     startkey
    }
    if limit != -1:
        args['limit'] = limit

    response = requests.get(view_url, params=args, auth=(username, password))
    data = response.json().get('rows')

    if limit == -1:
        return data

    if data is not None and len(data) > 0:
        return data[0].get('value')
    else:
        return None


def get_cloudant_document(doc_id):
    doc_url = database_url + '/' + doc_id
    response = requests.get(doc_url, auth=(username, password))
    return response.json()


def get_cloudant_attachment(doc_id):
    doc = get_cloudant_document(doc_id)
    if doc is None:
        return None

    filename = next(iter(doc['_attachments']))
    attachment_url = database_url + '/' + doc_id + '/' + filename

    response = requests.get(attachment_url, auth=(username, password))
    attachment = response.content
    return attachment


def post_cloudant_document(data):
    response = requests.post(database_url, json=data, auth=(username, password))
    return response


def get_next_document(timestamp):
    if timestamp is None or int(timestamp) == 0:
        doc = get_cloudant_view()
    else:
        doc = get_cloudant_view(skip=1, startkey=timestamp)
    return doc


def get_all_documents():
    docs = get_cloudant_view(limit=-1)
    return docs


def get_start_id():
    doc = get_next_document(None)
    doc_id = doc.get('_id')
    return doc_id


def get_rotate_degrees(orientation):
    if orientation == 3:
        degrees = 180
    elif orientation == 6:
        degrees = 270
    elif orientation == 8:
        degrees = 90
    else:
        degrees = 0

    return degrees


@app.route('/')
def main_page():
    return home_page()


@app.route('/home')
def home_page():
    return render_template('index.html')


@app.route('/display')
def display():
    return render_template('display.html')


@app.route('/view')
def view():
    return render_template('view.html')


@app.route('/upload', methods=['GET'])
def upload():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_slide():
    timestamp = int(time.time() * 1000)
    category = request.form['category']
    caption = request.form['caption']

    slide_data = {
        'timestamp':    timestamp,
        'category':     category,
        'caption':      caption
    }

    img_file = request.files[request.form['upload']]
    img_orientation = int(request.form['orientation'])

    img = Image.open(img_file)
    img = img.rotate(get_rotate_degrees(img_orientation), expand=True)

    resize_ratio = min(MAX_IMAGE_WIDTH / img.size[0], MAX_IMAGE_HEIGHT / img.size[1])

    if resize_ratio < 1:
        new_size = (int(img.size[0] * resize_ratio), int(img.size[1] * resize_ratio))
        img.thumbnail(new_size, Image.ANTIALIAS)

    img_buffer = BytesIO()
    img.save(img_buffer, format='JPEG')
    img_data = base64.b64encode(img_buffer.getvalue())

    attachment_data = {
        'upload{}.jpg'.format(timestamp): {
            'content-type':     'image/jpeg',
            'data':             img_data
        }
    }

    slide_data['_attachments'] = attachment_data

    post_cloudant_document(slide_data)

    return redirect(url_for('upload', success=True))


@app.route('/doc/recent', methods=['GET'])
def send_document():
    timestamp = request.args.get('time')
    doc = get_next_document(timestamp)
    if doc is not None:
        slide_data = {
            'id':           doc['_id'],
            'timestamp':    doc['timestamp'],
            'category':     doc['category'],
            'caption':      doc['caption']
        }
        return jsonify(slide_data)
    else:
        return jsonify({})


@app.route('/doc/all', methods=['GET'])
def send_all_documents():
    docs = get_all_documents()

    doc_array = []
    for i in range(len(docs)):
        img_id = docs[i]['value']['_id']
        doc_array.append(img_id)

    return jsonify(doc_array)


@app.route('/image/guest', methods=['GET'])
def send_guest_image():
    doc_id = request.args.get('id')
    if doc_id is None:
        doc_id = get_start_id()

    attachment = get_cloudant_attachment(doc_id)
    if attachment is not None:
        img_data = BytesIO(attachment)
        img_data.seek(0)

        return send_file(img_data, mimetype='image/jpeg')
    else:
        raise ValueError('The requested image is unavailable.')


@app.route('/image/host', methods=['GET'])
def send_host_image():
    img_id = int(request.args.get('id'))
    if img_id is None:
        img_id = 0
    elif img_id >= MAX_IMAGE_ID:
        raise ValueError('The requested image is unavailable.')

    return send_from_directory('static', 'images/wedding/photo' + str(img_id) + '.jpg')


@app.errorhandler(404)
def page_not_found(err):
    return render_template('err404.html')


@app.errorhandler(500)
def app_error(err):
    return render_template('err500.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, processes=5)
