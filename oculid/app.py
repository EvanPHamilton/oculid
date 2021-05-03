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

@app.route('/tester/<id>', methods=['GET'])
def tester(id):
    """
    Return a list of tester ids associated with a given
    test
    """
    logger("Tester called for id %s " % id)
    if request.method == 'GET':
        return get_tester_data(id)


@app.route('/tester/<id>/metadata', methods=['GET'])
def tester_metadata(id):
    """
    Return a list of tester ids associated with a given
    test
    """
    logger("Tester metadata called for id %s " % id)
    if request.method == 'GET':
        return get_tester_metadata(id)


@app.route('/test/<id>', methods=['GET'])
def test(id):
    """
    Return a list of tester ids associated with a given
    test
    """
    logger("Test called for id %s " % id)
    if request.method == 'GET':
        return get_testers(id)



@app.route('/upload', methods=['POST'])
def upload_file():
    logger("Upload called")
    if request.method == 'POST':
        # Compare set of files and expected files
        # prevent malicious files being parsed
        if set(request.files) != EXPECTED_FILES:
            # We may wish to use a more helpful error code in proudction
            abort(418, "Uploaded files do not match expected files")

        # First parse tester.json to create tester and
        # determine where to save subsequent data
        res, data = read_and_save_tester_json(request.files['tester.json'])
        if not res:
            abort(400, data)

        tester_id, tester_folder = data

        # Parse video.json, then save video file,
        # then set video path. Separated to make refactoring
        # with saving to something like S3 in mind.
        res, data = read_video_json_save_data(
                        request.files['video.json'],
                        tester_id)
        if not res:
            abort(400, data)

        video_id = data
        res = save_video_set_path(
                        request.files['video.mp4'],
                        video_id,
                        tester_folder)
        if not res:
            abort(400, "Unable to save video.mp4")


        # Parse pics.json, then save pic files,
        # then set pic paths. Separated to make refactoring
        # with saving to something like S3 in mind.
        res, data = parse_pic_json_save_data(
                        request.files['pics.json'],
                        tester_id)
        if not res:
            abort(400, data)

        # The rest of these functions are returning success codes,
        # based off data validation. Would introduce something similar going
        # forward for pictures. For now, assume the saving works or raises.
        pics_list = request.files.getlist('pics')
        save_pictures_set_pathes(pics_list, tester_id, tester_folder)

        # Check that the tester's pictures and video have paths set
        # as proxy for successful data upload
        tester = Tester.query.filter_by(id=tester_id).first()
        if not tester.pictures_uploaded or not tester.video_uploaded:
            abort(400, "Video or pictures not uploaded successfully")
        else:
            return "Success"