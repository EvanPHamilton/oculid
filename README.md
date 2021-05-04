Hey Oculid, here is my test project. 

I used flask to write my api. 

To get everything running there are a couple steps:

1. Set up a virtualenv, install dependencies requirements.txt

2. Run `python setup.py` to create db and data folder

3. `export FLASK_APP=oculid/app.py` to tell flask where to look

4. Finally `flask run` to start the server


Then if you want you can run  `python live_api_test.py` to fire some requests against the live endpoints, using the sample data you gave me.

If you run this more than once the requests will fail, as 
we hit some database uniqueness constraints. 

Project structure:

Most of the code lives in the oculid folder. There is a 
schemas.py file with the db schemas, an app.py file where
the routes are registered, and a data_management.py file, 
where the data is parsed, verified, and written/read from the db.

I wanted to write some tests to show I could, without taking the time to write full production coverage. These tests live in tests/tes_data_management.py. The tests can be run with 
`pytest`.