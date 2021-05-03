import requests
import json
import os

from time import perf_counter
from os import getcwd

cwd = getcwd()

BASEPATH = "http://127.0.0.1:5000/"
path_to_file = os.path.join(cwd,"oculid_backend_challenge/data/tester.json")
path_to_file1 = os.path.join(cwd,"oculid_backend_challenge/data/video.mp4")
path_to_file2 = os.path.join(cwd,"oculid_backend_challenge/data/video.json")
path_to_pics_json = os.path.join(cwd, "oculid_backend_challenge/data/pics.json")
path_to_pic_files = os.path.join(cwd, "oculid_backend_challenge/data/images")
upload_metadata = os.path.join(BASEPATH, "upload")
get_tests = os.path.join(BASEPATH, "test")

get_tester_metadata = os.path.join(BASEPATH, "tester", "1", "metadata")
get_tester_data = os.path.join(BASEPATH, "tester", "1")
get_tester = os.path.join(BASEPATH, "test")


# Test uploading all of the files for a single tester
with open(path_to_file, 'rb') as f1:
	with open(path_to_file1, 'rb') as f2:
		with open(path_to_file2, 'rb') as f3:
			with open(path_to_pics_json, 'rb') as f4:
				files = [
				    ('tester.json', f1),
				    ('video.mp4', f2),
				    ('video.json', f3),
				    ('pics.json', f4)
				]
				for file in os.listdir(path_to_pic_files):
					path_to_picture = os.path.join(path_to_pic_files, file)
					open_pic_file = open(path_to_picture, "rb")
					files.append(('pics', open_pic_file))

				t1_start = perf_counter()
				test_response = requests.post(upload_metadata, files=files)
				t1_stop = perf_counter()
				print("Elapsed time during upload in seconds:",
                                        t1_stop-t1_start)
				if test_response.status_code != 200:
					print(test_response.text)



# Test getting tester data
res = requests.get(get_tester_data)
assert res.status_code == 200
data = res.json()
print(data['result']['picture_paths'])


# Test getting tester metadata
res = requests.get(get_tester_metadata)
assert res.status_code == 200
print(res.json())

# Test getting test data
res = requests.get(get_tests+"/11")
assert res.status_code == 200
print(res.text)
