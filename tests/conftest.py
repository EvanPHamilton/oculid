import os
import tempfile
import pytest
from oculid import app


@pytest.fixture
def test_db(tmpdir):
	app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/test.db' % tmpdir
	app.app.config['UPLOAD_FOLDER'] = tmpdir
	app.db.create_all()
	yield app.db
	app.db.session.remove()
	app.db.drop_all()