import hashlib
import hmac
import io
import os
from base64 import b64encode

import cv2
import git
import numpy as np
from flask import Flask, redirect, render_template, request
from PIL import Image

import main

SECRET_TOKEN = os.getenv('SECRET_TOKEN')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploaded_images'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/segment', methods=['GET', 'POST'])
def segment():
    if request.method == 'POST':
        if (
            'file' not in request.files or
            not request.files['file'].filename or
            '.' not in request.files['file'].filename or
            request.files['file'].filename.split('.')[-1].lower() not in {
                'png', 'jpg', 'jpeg', 'gif'
            }
        ):
            return redirect(request.url)
        file = request.files['file']

        original_image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
        image = main.resize(original_image)
        res = "data:image/png;base64," + b64encode(cv2.imencode('.png', image)[1]).decode('ascii')

        output_1, output_2 = main.evaluate(image)

        seg_byt = io.BytesIO()
        seg_img = Image.fromarray((output_1 * 255).astype('uint8'))
        seg_img.save(seg_byt, 'PNG')
        seg = "data:image/png;base64," + b64encode(seg_byt.getvalue()).decode('ascii')

        ext_byt = io.BytesIO()
        ext_img = Image.fromarray((output_2 * 255).astype('uint8'))
        ext_img.save(ext_byt, 'PNG')
        ext = "data:image/png;base64," + b64encode(ext_byt.getvalue()).decode('ascii')
        return render_template('segment.html', res=res, seg=seg, ext=ext)
    return render_template('segment.html')


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        if is_valid_signature(request.headers.get('X-Hub-Signature'), request.data, SECRET_TOKEN):
            git.Repo('/home/wjm/PythonAnywhereApp').remotes.origin.pull()
            return 'Successful Server Update!', 200
        else:
            return 'Invalid Signature', 401
    else:
        return 'Wrong Method', 400


def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


if __name__ == '__main__':
    app.run(debug=True)
