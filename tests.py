import requests
import json
import os
from time import perf_counter

path_to_file = "/home/evan/oculid/oculid_backend_challenge/data/tester.json"
path_to_file1 = "/home/evan/oculid/oculid_backend_challenge/data/video.mp4"
path_to_file2 = "/home/evan/oculid/oculid_backend_challenge/data/video.json"
path_to_pics_json = "/home/evan/oculid/oculid_backend_challenge/data/pics.json"
path_to_pic_files = "/home/evan/oculid/oculid_backend_challenge/data/images"
upload_metadata = "http://127.0.0.1:5000/upload_metadata"
upload_pictures = "http://127.0.0.1:5000/upload_pictures"
upload_video = "http://127.0.0.1:5000/upload_video"


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
				data = test_response.json()
				print(data)
				user_id = data['result']['id']
