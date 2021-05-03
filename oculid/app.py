import logging
import sqlalchemy as alchemy

from flask import Flask, flash, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

from os import getcwd

cwd = getcwd()

UPLOAD_FOLDER = '%s/data_folder' % cwd
EXPECTED_FILES = set(['tester.json', 'video.mp4', 'pics',
                    'video.json', 'pics.json'])

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/v1.db' % cwd
db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
logger = app.logger.info

# Have to import after creating db app
# because data_management requires db
from oculid.data_management import *

"""
Register our routes down below
"""

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    logger("Upload called")
    if request.method == 'POST':
        # Compare set of files and expected files
        # prevent malicious files being parsed
        if set(request.files) != EXPECTED_FILES:
            # We may wish to use a more helpful error code in proudction
            abort(418, "Uploaded files do not match expected files")

        video_filepath = save_video(request.files['video.mp4'])
        res, data = read_and_save_tester_json(request.files['tester.json'])
        if not res:
            abort(400, data)

        tester_id = data
        res, data = parse_video_json_save_data(
                        request.files['video.json'],
                        video_filepath,
                        data)
        if not res:
            abort(400, data)

        res, data = parse_pic_json_save_data(
                        request.files['pics.json'], tester_id)
        if not res:
            abort(400, data)

        # The rest of these calls return True/False to indicate
        # success/failure based off some validation. No validation
        # of pic info yet
        pics_list = request.files.getlist('pics')
        save_pictures_set_pathes(pics_list, tester_id)

        tester = Tester.query.filter_by(id=tester_id).first()
        if not tester.pictures_uploaded or not tester.video_uploaded:
            abort(400, "Video and pictures not uploaded successfully")
        else:
            return "Success"