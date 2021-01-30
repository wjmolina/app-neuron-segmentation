import io
from base64 import b64encode

import cv2
import numpy as np
from flask import Flask, redirect, render_template, request
from PIL import Image

import main

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/segment', methods=['GET', 'POST'])
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
