rem del instance
rem del migrations

flask db init
flask db upgrade
flask db migrate 
flask db upgrade
flask db migrate 
flask db upgrade
flask db migrate 
flask run --debug