import oculid
from oculid import data_management

print(oculid)

def test_validate_video_json():
    """Test video json data validation"""
    res, msg = data_management._validate_video_json({})
    assert res is False
    assert msg == "Duration value not in video.json file"
