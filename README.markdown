# Altium Designer Library

A simple web-frontend for managing components in Altium Designer.  This is for you if you use database libraries, or SVNDBlib files, which use an external database to manage library components.

## Dependencies

    pip install -r requirements.txt #this works better in pip 8.3... might be more reliable to mkvirtualenv
    Maybe a running postgres server? Should not need to be postgres, but some backend is needed
    An SVN server

## Running

    python main.py

## Credits

Thanks to Ryan Sturmer who wrote the original application.

Thanks to Michael Fogleman of http://michaelfogleman.com who developed the HelloFlask starting point from which this application is derived.
