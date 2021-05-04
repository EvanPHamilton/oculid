import json
import os
from oculid import data_management


"""
Tests for data management
"""

def test_parse_pic_json_save_data(tmp_path, test_db):
	"""
	Test that parse_pic_json_save_data
	will write to the database
	"""

	pic=[{
	"height": 128,
	"time": 766677100045579,
	"width": 128,
	"pic_num": 0,
	"image_path": "./oculid_backend_challenge/images/0.png"
	}]
	tester_id=1
	filepath = os.path.join(tmp_path, "pics.json")
	with open(filepath, 'w') as testfile:
		json.dump(pic, testfile)
	with open(filepath, 'r') as openfile:
		res, msg = data_management.parse_pic_json_save_data(openfile, tester_id)
	assert res
	assert msg == "Pictures successfully added to database"
	picture = test_db.session.query(data_management.Picture).first()
	assert picture.height == 128


def test_read_json_file(tmp_path):
	"""
	Write a test json file
	Open it
	and test that read_json_file
	returns the contents as a dict
	"""

	json_data={'id': 10}
	filepath = os.path.join(tmp_path, "test.json")
	with open(filepath, 'w') as testfile:
		json.dump(json_data, testfile)

	with open(filepath, 'r') as openfile:
		data = data_management._read_json_file(openfile)
	assert json_data == data


# Data validation tests
# Not exhaustive
def test_validate_video_json_empty_file():
    """Validation should fail for empty file"""
    res, data = data_management._validate_video_json({})
    assert res is False
    assert data == "Duration value not in video.json file"

def test_validate_video_json_success():
    """Validation should success with duration and time
    int values."""
    res, data = data_management._validate_video_json({
    	'duration': 10,
    	'time': 10000
    	})
    assert res is True
    assert data == "success"

def test_validate_pic_json_empty():
	res, data = data_management._validate_pic_json({})
	assert res is False
	assert data == "Pic num missing from entry in pics.json"

def test_validate_pic_json_wrong_type():
	res, data = data_management._validate_pic_json({'pic_num': [10]})
	assert res is False
	assert data == "Pic num value not type int"

def test_validate_pic_json_success():
	res, data = data_management._validate_pic_json({
		'pic_num': 10,
		'height': 10,
		'width': 20,
		'time': 100,
		'image_path': "/test/"
		})
	assert res is True
	assert data == "success"

def test_validate_tester_json_empty():
	res, data = data_management._validate_tester_json({})
	assert res is False
	assert data == "Tester.json does not include all of the required keys"

valid_tester_json = {
		'test_id': 10,
		'screen_height': 10,
		'screen_width': 20,
		'phone_model': "galaxy",
		'phone_manufacturer': "samsung",
		'time': '2018-04-21T14:40:15+00:00'
		}

def test_validate_tester_json_success():
	res, data = data_management._validate_tester_json(valid_tester_json)
	assert res is True
	assert data == "success"

def test_validate_tester_json_wrong_type():
	valid_tester_json['screen_height'] = '20'
	res, data = data_management._validate_tester_json(valid_tester_json)
	assert res is False
	assert data == "screen_height type not value int"
	valid_tester_json['screen_height'] = 20

def test_validate_tester_json_wrong_time_format():
	valid_tester_json['time'] = '2018-04--21T14:40:15+00:00'
	res, data = data_management._validate_tester_json(valid_tester_json)
	assert res is False
	assert data == "Unable to parse time string into datetime"
	valid_tester_json['screen_height'] = 20



# The ‘time’ attribute for each Pic must be
#unique for a given tester