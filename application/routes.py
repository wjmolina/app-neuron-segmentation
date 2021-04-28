import io
import datetime
from base64 import b64encode

import michela.main as main
from flask import redirect, render_template, request
from PIL import Image
from flask_sqlalchemy import SQLAlchemy

from application import application

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)


class SegmentMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    used_datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)


db.create_all()


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/segment_metrics')
def segment_metrics():
    return render_template('segment_metrics.html', data=sorted(
        db.session.query(SegmentMetrics).all(),
        key=lambda x: x.used_datetime,
        reverse=True
    ))


@application.route('/segment', methods=['GET', 'POST'])
def segment():
    if request.method == 'POST':
        db.session.add(SegmentMetrics())
        db.session.commit()
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

        ori_img = Image.open(io.BytesIO(file.read()))
        image = ori_img.resize((512, 512))

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        res = "data:image/png;base64," + b64encode(buffered.getvalue()).decode('ascii')

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
