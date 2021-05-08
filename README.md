# audio-file-api
A sample API that simulates an audio file server.


# Running the application locally
* Rename the sample.ini file in config directory to config.ini
* Change options in ```MISC``` and ```DATABASE``` sections to appropriate values
* Change to src directory(Make sure virtualenv is active)
* ```python manage.py runserver```

# Running tests
* Change directory to src
* ```python manage.py test --verbosity 2```