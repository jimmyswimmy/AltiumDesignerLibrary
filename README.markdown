# Altium Designer Library

A simple web-frontend for managing components in Altium Designer.  This is for you if you use database libraries, or SVNDBlib files, which use an external database to manage library components.

## Dependencies

    - pip install -r requirements.txt #this works better in pip < 10.0
    - A database backend supported by SQLAlchemy.
    - An SVN server, filled with your symbols and footprints
    
## Database requirements
The database can contain anything you want. The original author uses reflection to see what's in each table. Nonetheless the database MUST include certain fields, including at least the following:

    - uuid (must be the primary key)
    - id
    - library_ref
    - footprint_ref
    - status
    
Both uuid and id will not be shown in any of the displays. You'll never know they're there. But if uuid is not the primary key, almost nothing will work right. Particularly the copy part/edit part features.
    
If you use a sqlite database, the process must have rw access to it. I usually chmod 644 it. If you put it in the altium directory, you can refer to it as sqlite:///database.sqlite, however there are probably lots of reasons to avoid doing this. In particular only one write at a time is supported by sqlite, so if you have a lot of users that's a bad idea.

## Running

    python3 main.py

## Credits

Thanks to Ryan Sturmer who wrote the original application.

Thanks to Michael Fogleman of http://michaelfogleman.com who developed the HelloFlask starting point from which this application is derived.
