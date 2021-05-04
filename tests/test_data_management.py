from oculid import data_management

"""
Tests for data management
"""


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