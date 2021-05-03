from flask import Flask, flash, request, redirect, url_for
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

expected_files = ['tester.json', 'video.mp4', 'video.json', 'pics.json', 'pics']


@app.route('/upload_metadata', methods=['GET', 'POST'])
def upload_file():
    app.logger.info("Upload called")
    if request.method == 'POST':
        for file in expected_files:
            if file not in request.files:
                # We might wish to use a more helpful status code in production
                return 418
        video_filepath = save_video(request.files['video.mp4'])
        tester_id = parse_and_save_tester_json(request.files['tester.json'])
        res, err_msg = parse_video_json_save_data(
                        request.files['video.json'],
                        video_filepath,
                        tester_id)
        if not res:
            return "Problem with video.json file: %s " % err_msg

        res, err_msg = parse_pic_json_save_data(
            request.files['pics.json'], tester_id)

        pics_list = request.files.getlist('pics')
        res, err_msg = save_pictures_set_pathes(pics_list, tester_id)


        if not res:
            return "Problem with pic.json file: %s " % err_msg

        res = {"err_msg": None, "result": {"id": tester_id}}
        return jsonify(res)