import os
from oculid.app import db


"""
This file handles first time set up
of the application, creating the db file
and data folder if neccessary.
"""


cwd = os.getcwd()
DATA_FOLDER = os.path.join(cwd, "data_folder")
if not os.path.exists(DATA_FOLDER):
	os.makedirs(DATA_FOLDER)

db.create_all()
