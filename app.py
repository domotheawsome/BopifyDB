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
os.environ['340DBPW'] = '7096'
os.environ['340DB'] = 'cs340_meshorea'

host = os.environ.get("340DBHOST")
user = os.environ.get("340DBUSER")
passwd = os.environ.get("340DBPW")
db = os.environ.get("340DB")

def connect_to_database(host = host, user = user, passwd = passwd, db = db):
    '''
    connects to a database and returns a database objects
    '''
    db_conn = MySQLdb.connect(host,user,passwd,db)
    return db_conn

def execute_query(db_connection = None, query = None, query_params = ()):
    '''
    executes a given SQL query on the given db connection and returns a Cursor object

    db_connection: a MySQLdb connection object created by connect_to_database()
    query: string containing SQL query

    returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
    You need to run .fetchall() or .fetchone() on that object to actually acccess the results.

    '''
    print("inside this function")
    if db_connection is None:
        print("No connection to the database found! Have you called connect_to_database() first?")
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params));
    # Create a cursor to execute query. Why? Because apparently they optimize execution by retaining a reference according to PEP0249
    #cursor = db_connection.cursor()
    cursor = db_connection.cursor(MySQLdb.cursors.DictCursor)

    '''
    params = tuple()
    #create a tuple of paramters to send with the query
    for q in query_params:
        params = params + (q)
    '''
    #TODO: Sanitize the query before executing it!!!
    cursor.execute(query, query_params)
    # this will actually commit any changes to the database. without this no
    # changes will be committed!
    db_connection.commit();
    return cursor

db_connection = connect_to_database(host,user,passwd,db)
cursor = db_connection.cursor(MySQLdb.cursors.DictCursor)
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
    db_connection = connect_to_database(host,user,passwd,db)
    #cursor = db_connection.cursor(MySQLdb.cursors.DictCursor)
    #cursor = db_connection.cursor()
    query = 'SELECT * FROM bsg_people;'
    #cursor.execute(query)
    #results = cursor.fetchall()
    results = execute_query(db_connection=db_connection, query=query).fetchall()
    # write the query and save it to a variable
    #print(query)
    #results = db.execute_query(db_connection=db_connection, query=query).fetchall()
    #result = execute_query(db_connection, query, data)
    #results = cursor.fetchall()
    #return("This is the bsg-people routine.")
    print(results)
    return render_template("bsg2.j2", bsg_people=results)

# Listener

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9117, debug=True)