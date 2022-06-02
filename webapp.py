from flask import Flask, render_template
from flask import request, redirect
from database.db_connector import connect_to_database, execute_query


#import database.db_connector as db
#create the web application
webapp = Flask(__name__)

#provide a route where requests on the web application can be addressed
@webapp.route('/hello')
#provide a view (fancy name for a function) which responds to any requests on this route
def hello():
    return "Hello World!"

@webapp.route('/')
def index():
    return render_template('index.html')

@webapp.route('/home')
def home():
    db_connection = connect_to_database()
    query = "DROP TABLE IF EXISTS diagnostic;"
    execute_query(db_connection, query)
    query = "CREATE TABLE diagnostic(id INT PRIMARY KEY, text VARCHAR(255) NOT NULL);"
    execute_query(db_connection, query)
    query = "INSERT INTO diagnostic (text) VALUES ('MySQL is working');"
    execute_query(db_connection, query)
    query = "SELECT * from diagnostic;"
    result = execute_query(db_connection, query)
    for r in result:
        print(f"{r[0]}, {r[1]}")
    return render_template('home.html', result = result)

@webapp.route('/db_test')
def test_database_connection():
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = "SELECT * from bsg_people;"
    result = execute_query(db_connection, query)
    return render_template('db_test.html', rows=result)



@webapp.route('/people')
def people():
    print("Fetching and rendering people web page")
    db_connection = connect_to_database()
    query = "SELECT fname, lname, homeworld, age, id from bsg_people;"
    result = execute_query(db_connection, query).fetchall()
    planetquery = 'SELECT id, name from bsg_planets'
    planetresult = execute_query(db_connection, planetquery).fetchall()
    print(result)
    print(planetresult)


    return render_template('people.html', rows=result,planets=planetresult)


@webapp.route('/people_functionality/', methods=['GET', 'POST'])
def people_functionality():
    
    db_connection = connect_to_database()

    peoplequery = "SELECT fname, lname, homeworld, age, id from bsg_people;"
    peopleresult = execute_query(db_connection, peoplequery).fetchall()
    print(peopleresult)

    planetquery = 'SELECT id, name from bsg_planets'
    planetresult = execute_query(db_connection, planetquery).fetchall()
    print(planetresult)


    if "Submit" in request.form:
        print("Add new people!")
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        insertquery = 'INSERT INTO bsg_people (fname, lname, age, homeworld) VALUES (%s,%s,%s,%s)'
        insertdata = [fname, lname, age, homeworld]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            error = f"Error: {e.args[1]}" 
            return  render_template('people.html', rows=result, planets=planetresult, data=error)


                # print out a message to let the user know a cashier was added
        insertresult = f"Person Added: {fname} {lname}"

        # query to get new data
        query = "SELECT fname, lname, homeworld, age, id from bsg_people;"
        result = execute_query(db_connection, query)

        return  render_template('people.html', rows=result, planets=planetresult, insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    elif "Search" in request.form:
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        searchdata=(fname, lname, age)
        searchquery="SELECT * from bsg_people where fname=%s and lname=%s and age=%s"
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('people.html', rows=result, planets=planetresult, data=error)
        return  render_template('people.html', rows=searchresult, planets=planetresult)
    elif "Return" in request.form:
        return redirect('/people')

        

@webapp.route('/browse_bsg_people')
#the name of this function is just a cosmetic thing
def browse_people():
    print("Fetching and rendering people web page")
    db_connection = connect_to_database()
    query = "SELECT fname, lname, homeworld, age, id from bsg_people;"
    result = execute_query(db_connection, query).fetchall()
    print(result)
    return render_template('people_browse.html', rows=result)

@webapp.route('/add_new_people', methods=['POST','GET'])
def add_new_people():
    db_connection = connect_to_database()
    cursor = db_connection.cursor()



    if request.method == 'GET':
        query = 'SELECT id, name from bsg_planets'
        result = execute_query(db_connection, query).fetchall()
        print(result)

        return render_template('people_add_new.html', planets = result)
    elif request.method == 'POST':
        print("Add new people!")
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        query = 'INSERT INTO bsg_people (fname, lname, age, homeworld) VALUES (%s,%s,%s,%s)'
        data = [fname, lname, age, homeworld]

        # check for null/empty data
        index = 0
        for d in data:
            if d == '':
                data[index] = None
            index += 1

        execute_query(db_connection, query, data)
        return redirect('/browse_bsg_people')

#display update form and process any updates, using the same function
@webapp.route('/update_people/<int:id>', methods=['POST','GET'])
def update_people(id):
    print('In the function')
    db_connection = connect_to_database()
    #display existing data
    if request.method == 'GET':
        print('The GET request')
        people_query = 'SELECT id, fname, lname, homeworld, age from bsg_people WHERE id = %s'  % (id)
        people_result = execute_query(db_connection, people_query).fetchone()

        if people_result == None:
            return "No such person found!"

        planets_query = 'SELECT id, name from bsg_planets'
        planets_results = execute_query(db_connection, planets_query).fetchall()

        print('Returning')
        return render_template('people_update.html', planets = planets_results, person = people_result)
    elif request.method == 'POST':
        print('The POST request')
        id = request.form['id']
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        query = "UPDATE bsg_people SET fname = %s, lname = %s, age = %s, homeworld = %s WHERE id = %s"
        data = (fname, lname, age, homeworld, id)
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        return redirect('/people')

@webapp.route('/delete_people/<int:id>')
def delete_people(id):
    '''deletes a person with the given id'''
    db_connection = connect_to_database()
    query = "DELETE FROM bsg_people WHERE id = %s"
    data = (id,)

    result = execute_query(db_connection, query, data)
    return redirect('/people')