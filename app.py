from importlib.util import resolve_name
import os
import MySQLdb
from dotenv import load_dotenv
from flask import Flask, request, render_template
import configparser

people_from_app_py = [
{
    "name": "Thomas",
    "age": 33,
    "location": "New Mexico",
    "favorite_color": "Blue"
},
{
    "name": "Gregory",
    "age": 41,
    "location": "Texas",
    "favorite_color": "Red"
},
{
    "name": "Vincent",
    "age": 27,
    "location": "Ohio",
    "favorite_color": "Green"
},
{
    "name": "Alexander",
    "age": 29,
    "location": "Florida",
    "favorite_color": "Orange"
}
]

# Configuration
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
app = Flask(__name__)

# Routes 
@app.route('/')
def root():
    return render_template("main.j2", people=people_from_app_py)

@app.route('/bsg-people')
def bsg_people():
    cursor = db_connection.cursor()
    query = 'SELECT * FROM bsg_people;'
    cursor.execute(query)
    results = cursor.fetchall()
    # write the query and save it to a variable
    #print(query)
    #results = db.execute_query(db_connection=db_connection, query=query).fetchall()
    #result = execute_query(db_connection, query, data)
    #results = cursor.fetchall()
    #return("This is the bsg-people routine.")

    return render_template("bsg2.j2", bsg_people=results)

# Listener

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9117, debug=True)