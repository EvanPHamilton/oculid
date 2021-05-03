import os

from flask import json
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from schema import Tester, Test, Video, Picture
from app import db, UPLOAD_FOLDER, logger

EXPECTED_DATA = set(['test_id', 'time', 'phone_manufacturer',
            'phone_model', 'screen_height', 'screen_width'])
SQL_UNIQUENESS_ERROR = "UNIQUE constraint failed: picture.tester_id, picture.time"

def save_pictures_set_pathes(pics_list, tester_id):
    """
    pic list  -- list of werkzeug.datastructures.FileStorage
    tester_id -- int
    """
    for pic in pics_list:
        pic_number = pic.filename.split(".")[0]
        path = save_pic(pic, tester_id)
        set_path(tester_id, pic_number, path)

    # Only commit once to avoid
    # database overhead, optimize later
    db.session.commit()
    return True, "Success"


def save_pic(pic, tester_id):
    """
    pic       - werkzeug.datastructures.FileStorage
    tester_id - int
    Saves an open filestream and returns the path
    where it was saved
    """
    filename = secure_filename(pic.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    pic.save(path)
    return path

def set_path(tester_id, pic_num, path):
    """
    pic       - werkzeug.datastructures.FileStorage
    tester_id - int
    Saves an open filestream and returns the path
    """
    picture = Picture.query.filter_by(tester_id=tester_id, pic_num=pic_num).first()
    picture.image_path = path


def save_video(video_file):
    filename = secure_filename(video_file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    video_file.save(filepath)
    return filepath


def _validate_video_json(video_json):
    try:
        assert 'duration' in video_json, "Duration value not in video.json file"
        assert type(video_json['duration']) == int, "Duration value not type int"
        assert 'time' in video_json, "Time value no in video.json file"
        assert type(video_json['time']) == int, "Time value not type int"
    except AssertionError as e:
        return False, e
    return True, "success"

def parse_video_json_save_data(video_json, video_path, tester_id):
    """
    Read in the video.json file,
    Validate the file has the correct information,
    Create a new video entity in the db
    """

    # Read the file and load as json
    video_json.seek(0)
    video_json = json.loads(video_json.read())
    res, err_msg = _validate_video_json(video_json)
    if not res:
        return res, err_msg

    video = Video(
    duration=video_json['duration'],
    time=video_json['time'],
    video_path=video_path,
    tester_id=tester_id)
    db.session.add(video)
    db.session.commit()

    return True, "Success"

def validate_pic_json(pic):
    try:
        assert 'pic_num' in pic, \
            "Pic num missing from entry in pics.json"
        assert type(pic['pic_num']) == int, \
            "Pic num value not type int"
        assert 'height' in pic, \
            "Height value missing for pic %s from pics.json" % pic['pic_num']
        assert type(pic['height']) == int, \
            "Pic num value not type int for pic %s in pics.json" % pic['pic_num']
        assert 'width' in pic, \
            "Width value missing for pic %s from pics.json" % pic['pic_num']
        assert type(pic['width']) == int, \
            "Pic num value not type int"
        assert 'time' in pic, \
            "Time value missing for pic %s from pics.json" % pic['pic_num']
        assert type(pic['time']) == int, \
            "Time value not type for pic %s from pics.json" % pic['pic_num']
        assert 'image_path' in pic, \
            "image_path value missing for pic %s in pics.json" % pic['pic_num']

    except AssertionError as e:
        return False, e
    return True, "success"

def parse_pic_json_save_data(pics_json, tester_id):
    """
    Read the pics.json file,
    Validate the file has correct info and unique
    timestamps per pic
    Create new picture entities in the db
    """

    # Read the file and load as json
    pics_json.seek(0)
    pics_json = json.loads(pics_json.read())
    for pic in pics_json:
        res, err_msg = validate_pic_json(pic)
        if not res:
            return False, err_msg
        try:
            pic = Picture(
                height=pic['height'],
                width=pic['width'],
                pic_num=pic['pic_num'],
                time=pic['time'],
                tester_id=tester_id)
            db.session.add(pic)
            db.session.commit()
        except alchemy.exc.IntegrityError as e:
            if SQL_UNIQUENESS_ERROR in str(e):
                return False, "Time value for pic %s was not unique" % pic.pic_num
            else:
                return False, "Error storing picture data, please contact occulid"
    return True, "Pictures successfully added to database"


def read_and_save_tester_json(tester_json):
    """
    Parse tester_json file uploaded from user
    Save JSON file on filesystem
    Save tester in db
    """

    tester_json.save(os.path.join(UPLOAD_FOLDER,
        secure_filename(tester_json.filename)))
    # tester_json is an open file
    # seek(0) begins reading the file from the begining
    # TODO understand why we are not at the begining to start with
    tester_json.seek(0)
    tester = json.loads(tester_json.read())

    # Check that the data looks as we expect
    res, data = validate_tester_json(tester)
    logger(res)
    logger(data)
    if not res:
        return res, data

    # Open question how we want to handle posting test results
    # for non-existing test. For the sake of not losing data, I will
    # create a test if it does not exist
    test_exists = db.session.query(Test.id).filter_by(
                    id=tester['test_id']).first() is not None
    if not test_exists:
        test = Test(id=tester['test_id'])
        db.session.add(test)

    new_tester = Tester(
    test_id=tester['test_id'],
    time=tester['time'],
    phone_manufacturer=tester['phone_manufacturer'],
    phone_model=tester['phone_model'],
    screen_height=tester['screen_height'],
    screen_width=tester['screen_width'])
    db.session.add(new_tester)
    db.session.commit()
    return True, new_tester.id


def validate_tester_json(tester):
    keys = set(tester.keys())
    if keys != EXPECTED_DATA:
        return False, "Tester.json does not include all of the required keys"

    try:
        assert type(tester['test_id']) is int, \
                    "test_id type not value int"
        assert type(tester['screen_height']) is int, \
                    "screen_height type not value int"
        assert type(tester['screen_width']) is int, \
                    "screen_width type not value int"
        assert type(tester['phone_model']) is str, \
                    "phone_model type not value str"
        assert type(tester['phone_manufacturer']) is str, \
                    "phone_manufacturer type not value str"
    except AssertionError as e:
        return False, str(e)

    # time represented as '2018-04-21T14:40:15+00:00'
    # This cannot be parsed by strptime in python 3.5+
    # stptime expects no ":" in the 4 character timezone offset.
    # Add the ":" so we can parse/store as a datetime
    # If we can't reformat into datetime, fail and alert user
    try:
        time = tester['time']
        if time[-3] == ":":
            time = time[0:-3]+time[-2:]
        else:
            raise
        tester['time'] = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
    except Exception as e:
        # Generally I wouldn't want to except ANY exception
        return False, "Unable to parse time string into datetime"

    return True, "success"
