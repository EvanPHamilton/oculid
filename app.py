from flask import Flask, flash, request, redirect, url_for, abort
import logging
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as alchemy
from flask import jsonify
from os import getcwd


logging.basicConfig(level=logging.DEBUG)
cwd = getcwd()

UPLOAD_FOLDER = '%s/data_folder' % cwd
ALLOWED_EXTENSIONS = {'json', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/v1.db' % cwd
db = SQLAlchemy(app)
logger = app.logger.info

# Have to import after creating db app
from data_management import *
expected_files = ['tester.json', 'video.mp4', 'video.json', 'pics.json']


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    app.logger.info("Upload called")
    if request.method == 'POST':
        for file in expected_files:
            if file not in request.files:
                # We might wish to use a more helpful status code in production
                abort(418)

        video_filepath = save_video(request.files['video.mp4'])
        res, data = read_and_save_tester_json(request.files['tester.json'])
        if not res:
            res = {"err_msg": data, "result": None}
            return jsonify(res)

        tester_id = data
        res, data = parse_video_json_save_data(
                        request.files['video.json'],
                        video_filepath,
                        data)
        if not res:
            res = {"err_msg": data, "result": None}
            return jsonify(res)

        res, err_msg = parse_pic_json_save_data(
                        request.files['pics.json'], tester_id)


        pics_list = request.files.getlist('pics')
        res, err_msg = save_pictures_set_pathes(pics_list, tester_id)
        if not res:
            res = {"err_msg": None, "result": {"id": tester_id}}
            return jsonify(res)

        tester = Tester.query.filter_by(id=tester_id).first()
        if not tester.pictures_uploaded or not tester.video_uploaded:
            res = {"err_msg": None, "result": None}
        else:
            res = {"err_msg": None, "result": {"id": tester_id}}
            return jsonify(res)