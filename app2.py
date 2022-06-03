from importlib.util import resolve_name
import os
import MySQLdb
from dotenv import load_dotenv
from flask import Flask, request, render_template
import configparser


os.environ['340DBHOST'] = 'classmysql.engr.oregonstate.edu'
os.environ['340DBUSER'] = 'cs340_meshorea'
os.environ['340DBPW'] = ''
os.environ['340DB'] = 'cs340_meshorea'

host = os.environ.get("340DBHOST")
user = os.environ.get("340DBUSER")
passwd = os.environ.get("340DBPW")
db = os.environ.get("340DB")

def connect_to_database(host,user,passwd,db):
    '''
    connects to a database and returns a database objects
    '''
    db_conn = MySQLdb.connect(host,user,passwd,db)
    return db_conn

db_connection = connect_to_database(host,user,passwd,db)
cursor = db_connection.cursor()
cursor.execute("SET SESSION wait_timeout=31536000")
cursor.execute("SET SESSION interactive_timeout=31536000")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.connection.autocommit(True)



# just in case we have CORS issues
app = Flask(__name__)

# replace with your own login credentials file
db_connection = connect_to_database(host,user,passwd,db)
cursor = db_connection.cursor()
cursor.execute("SET SESSION wait_timeout=31536000")
cursor.execute("SET SESSION interactive_timeout=31536000")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.connection.autocommit(True)


@app.route('/bsg_people', methods=['GET', 'PUT', 'DELETE', 'POST'])
def get_bsg_people():
    '''
    returns all bsg_people in the database
    '''
    if request.method == 'GET':
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM bsg_people;")
        # db_connection.commit();

        response = {
            'data': [{
                'character_id': character_id,
                'fname': fname,
                'lname': lname,
                'homeworld': homeworld,
                'age': age,
                'race': race
            
            } for (character_id, fname, lname, homeworld, age, race) in cursor.fetchall()]
        }
        cursor.close()
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9114, debug=True)