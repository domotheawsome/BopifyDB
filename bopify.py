

from importlib.util import resolve_name
import os
import MySQLdb
from dotenv import load_dotenv
from flask import Flask, request, render_template,redirect
import configparser



##### DATABASE CONFIGURATION ######

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

#create the web application
bopify = Flask(__name__)


##########################################






#provide a route where requests on the web application can be addressed
@bopify.route('/hello')
#provide a view (fancy name for a function) which responds to any requests on this route
def hello():
    return "Hello World!"

@bopify.route('/')
def index():
    return render_template('index.html')

@bopify.route('/home')
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
    #for r in result:
     #   print(f"{r[0]}, {r[1]}")
    return render_template('home.html', result = result)

@bopify.route('/db_test')
def test_database_connection():
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = "SELECT * from bsg_people;"
    result = execute_query(db_connection, query)
    return render_template('db_test.html', rows=result)


############ ARTIST FUNCTIONALITY ###################

@bopify.route('/artists')
def artists():
    print("Fetching and rendering artists web page")
    db_connection = connect_to_database(host,user,passwd,db)
    query = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    result = execute_query(db_connection, query).fetchall()
    print(result)


    return render_template('artists.html', rows=result)


@bopify.route('/artists_functionality/', methods=['GET', 'POST'])
def artists_functionality():
    
    db_connection = connect_to_database(host,user,passwd,db)

    artistsquery = "SELECT artist_fname, artist_lname, artist_ID from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)


    if "Submit" in request.form:
        print("Add new Artists!")
        print(request.form)
        artist_fname = request.form['artist_fname']
        print(artist_fname)
        artist_lname = request.form['artist_lname']

        insertquery = 'INSERT INTO Artists (artist_fname, artist_lname) VALUES (%s,%s)'
        insertdata = [artist_fname, artist_lname]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            error = f"Error: {e.args[1]}" 
            return  render_template('artists.html', rows=result, data=error)


                # print out a message to let the user know a cashier was added
        insertresult = f"Artist Added: {artist_fname} {artist_lname}"

        # query to get new data
        query = "SELECT artist_fname, artist_lname, artist_ID from Artists;"
        result = execute_query(db_connection, query)

        return  render_template('artists.html', rows=result,  insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    elif "Search" in request.form:
        artist_fname = request.form['artist_fname']
        artist_lname = request.form['artist_lname']
    
        searchdata=(artist_fname, artist_lname)
        searchquery="SELECT * from Artists where artist_fname=%s or artist_lname=%s"
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        except Exception as e:
            error= f"Error: {e.args[1]}"
            return render_template('artists.html', rows=result, data=error)
        return  render_template('artists.html', rows=searchresult)
    elif "Return" in request.form:
        return redirect('/artists')

  
#display update form and process any updates, using the same function
@bopify.route('/update_artists/<int:artist_ID>', methods=['POST','GET'])
def update_artists(artist_ID):
    print('In the function')
    db_connection = connect_to_database(host,user,passwd,db)
    #display existing data
    if request.method == 'GET':
        print('The GET request')
        artists_query = 'SELECT artist_ID, artist_fname, artist_lname from Artists WHERE artist_ID = %s'  % (artist_ID)
        artists_result = execute_query(db_connection, artists_query).fetchone()

        if artists_result == None:
            return "No such person found!"


        print('Returning')
        return render_template('artists_update.html', artist = artists_result)
    elif request.method == 'POST':
        print('The POST request')
        artist_ID = request.form['artist_ID']
        artist_fname = request.form['artist_fname']
        artist_lname = request.form['artist_lname']

        query = "UPDATE Artists SET artist_fname = %s, artist_lname = %s WHERE artist_ID = %s"
        data = (artist_fname, artist_lname, artist_ID)
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        return redirect('/artists')

@bopify.route('/delete_artists/<int:artist_ID>')
def delete_artists(artist_ID):
    '''deletes an artist with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    query = "DELETE FROM Artists WHERE artist_ID = %s"
    data = (artist_ID,)

    execute_query(db_connection, query, data)
    return redirect('/artists')


#################### END ARTISTS #####################


################ ALBUM FUNCTIONALITY #################


@bopify.route('/albums')
def albums():


    print("Fetching and rendering albums web page")
    db_connection = connect_to_database(host,user,passwd,db)
    query = "SELECT album_name, album_genre, artist_ID, album_ID from Albums;"
    result = execute_query(db_connection, query).fetchall()
    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(result)
    print(artistsresult)


    return render_template('albums.html', rows=result,artists=artistsresult)


@bopify.route('/albums_functionality/', methods=['GET', 'POST'])
def albums_functionality():
    
    db_connection = connect_to_database(host,user,passwd,db)

    albumsquery = "SELECT album_name, album_genre, artist_ID, album_ID from Albums;"
    albumsresult = execute_query(db_connection, albumsquery).fetchall()
    print(albumsresult)

    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)


    if "Submit" in request.form:
        print("Add new albums!")
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']
        artist_ID = request.form['artist_ID']

        insertquery = 'INSERT INTO Albums (album_name, album_genre, artist_ID) VALUES (%s,%s,%s)'
        insertdata = [album_name, album_genre, artist_ID]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            error = f"Error: {e.args}" 
            return  render_template('albums.html', rows=albumsresult, artists=artistsresult, data=error)


                # print out a message to let the user know a cashier was added
        insertresult = f"Album Added: {album_name} {album_genre}"

        # query to get new data
        albumsquery = "SELECT album_name, album_genre, artist_ID, album_ID from Albums;"
        albumsresult = execute_query(db_connection, albumsquery).fetchall()
        print(albumsresult)

        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()

        return  render_template('albums.html', rows=albumsresult, artists=artistsresult, insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    elif "Search" in request.form:
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']

        searchdata=(album_name, album_genre)
        searchquery="SELECT * from Albums where album_name=%s or album_genre=%s "
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('albums.html', rows=albumsresult, artists=artistsresult, data=error)
        return  render_template('albums.html', rows=searchresult, artists=artistsresult)
    elif "Return" in request.form:
        return redirect('/albums')

        

#display update form and process any updates, using the same function
@bopify.route('/update_albums/<int:id>', methods=['POST','GET'])
def update_albums(id):
    print('In the function')
    db_connection = connect_to_database(host,user,passwd,db)
    #display existing data
    if request.method == 'GET':
        print('The GET request')
        albums_query = 'SELECT album_name, album_genre, artist_ID, album_ID from Albums WHERE album_ID = %s'  % (id)
        albums_result = execute_query(db_connection, albums_query).fetchone()

        if albums_result == None:
            return "No such album found!"
        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()

        print('Returning')
        return render_template('albums_update.html', artists = artistsresult, album = albums_result)
    elif request.method == 'POST':
        print('The POST request')
        album_ID = request.form['album_ID']
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']
        artist_ID = request.form['artist_ID']
        data = (album_name, album_genre, artist_ID, album_ID)
        query = "UPDATE Albums SET album_name = %s, album_genre = %s, artist_ID = %s WHERE album_ID = %s"
    
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        return redirect('/albums')

@bopify.route('/delete_albums/<int:id>')
def delete_albums(id):
    '''deletes a person with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    query = "DELETE FROM Albums WHERE album_ID = %s"
    data = (id,)

    result = execute_query(db_connection, query, data)
    return redirect('/albums')


#################### END ALBUMS ######################


################ SONGS FUNCTIONALITY #################



@bopify.route('/songs')
def songs():


    print("Fetching and rendering songs web page")
    db_connection = connect_to_database(host,user,passwd,db)
    query = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs;"
    result = execute_query(db_connection, query).fetchall()
    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)
    albumsquery = "SELECT album_ID, album_name from Albums;"
    albumsresult = execute_query(db_connection, albumsquery).fetchall()
    print(albumsresult)

    return render_template('songs.html', rows=result, albums=albumsresult, artists=artistsresult)


@bopify.route('/songs_functionality/', methods=['GET', 'POST'])
def songs_functionality():
    
    db_connection = connect_to_database(host,user,passwd,db)

    songsquery = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs;"
    songsresult = execute_query(db_connection, songsquery).fetchall()
    print(songsresult)

    albumsquery = "SELECT album_name, album_ID from Albums;"
    albumsresult = execute_query(db_connection, albumsquery).fetchall()
    print(albumsresult)

    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)


    if "Submit" in request.form:
        print("Add new songs!")
        song_name = request.form['song_name']
        song_genre = request.form['song_genre']
        artist_ID = request.form['artist_ID']
        album_ID = request.form['album_ID']

        insertquery = 'INSERT INTO Songs (song_name, song_genre, artist_ID, album_ID) VALUES (%s,%s,%s,%s)'
        insertdata = [song_name, song_genre, artist_ID, album_ID]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            error = f"Error: {e.args}" 
            return  render_template('songs.html', rows=songsresult, albums=albumsresult, artists=artistsresult, data=error)


                # print out a message to let the user know a cashier was added
        insertresult = f"Song Added: {song_name} {song_genre}"

        # query to get new data
        songsquery = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs;"
        songsresult = execute_query(db_connection, songsquery).fetchall()
        print(songsresult)

        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()
        print(artistsresult)
        albumsquery = "SELECT album_name, album_ID from Albums;"
        albumsresult = execute_query(db_connection, albumsquery).fetchall()
        print(albumsresult)
        return render_template('songs.html', rows=songsresult,albums=albumsresult, artists=artistsresult, insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    elif "Search" in request.form:
        song_name = request.form['song_name']
        song_genre = request.form['song_genre']

        searchdata=(song_name, song_genre)
        searchquery="SELECT * from Songs where song_name=%s or song_genre=%s "
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('songs.html', rows=songsresult, albums=albumsresult, artists=artistsresult, data=error)
        return  render_template('songs.html', rows=searchresult, albums=albumsresult, artists=artistsresult)
    elif "Return" in request.form:
        return redirect('/songs')

        

#display update form and process any updates, using the same function
@bopify.route('/update_songs/<int:id>', methods=['POST','GET'])
def update_songs(id):
    print('In the function')
    db_connection = connect_to_database(host,user,passwd,db)
    #display existing data
    if request.method == 'GET':
        print('The GET request')
        songsquery = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs WHERE song_ID = %s;" % (id)
        songsresult = execute_query(db_connection, songsquery).fetchone()
        print(songsresult)

        if songsresult == None:
            return "No such song found!"
        albums_query = 'SELECT album_name, album_ID from Albums;'
        albums_result = execute_query(db_connection, albums_query).fetchall()

        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()

        print('Returning')
        return render_template('songs_update.html', song = songsresult, artists = artistsresult, albums = albums_result)
    elif request.method == 'POST':
        print('The POST request')
        song_ID = request.form['song_ID']
        song_name = request.form['song_name']
        song_genre = request.form['song_genre']
        album_ID = request.form['album_ID']
        artist_ID = request.form['artist_ID']
        data = (song_name, song_genre, album_ID, artist_ID, song_ID)
        query = "UPDATE Songs SET song_name = %s, song_genre = %s, album_ID = %s, artist_ID = %s WHERE song_ID = %s"
    
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        return redirect('/songs')

@bopify.route('/delete_songs/<int:id>')
def delete_songs(id):
    '''deletes a person with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    query = "DELETE FROM Songs WHERE song_ID = %s"
    data = (id,)

    result = execute_query(db_connection, query, data)
    return redirect('/songs')



#################### END SONGS ######################

############### USER FUNCTIONALITY ##################


@bopify.route('/users')
def users():
    print("Fetching and rendering artists web page")
    db_connection = connect_to_database(host,user,passwd,db)
    query = "SELECT user_ID, user_name, user_email from Users;"
    result = execute_query(db_connection, query).fetchall()
    print(result)


    return render_template('users.html', rows=result)


@bopify.route('/users_functionality/', methods=['GET', 'POST'])
def users_functionality():
    
    db_connection = connect_to_database(host,user,passwd,db)

    usersquery = "SELECT artist_fname, artist_lname, artist_ID from Artists;"
    usersresult = execute_query(db_connection, usersquery).fetchall()
    print(usersresult)


    if "Submit" in request.form:
        print("Add new Users!")
        print(request.form)
        user_name = request.form['user_name']
        user_email = request.form['user_email']

        insertquery = 'INSERT INTO Users (user_name, user_email) VALUES (%s,%s)'
        insertdata = [user_name, user_email]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            error = f"Error: {e.args[1]}" 
            return  render_template('users.html', rows=result, data=error)


                # print out a message to let the user know a cashier was added
        insertresult = f"User Added: {user_name} {user_email}"

        # query to get new data
        query = "SELECT user_name, user_email, user_ID from Users;"
        result = execute_query(db_connection, query)

        return  render_template('users.html', rows=result,  insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    elif "Search" in request.form:
        user_name = request.form['user_name']
        user_email = request.form['user_email']
    
        searchdata=(user_name, user_email)
        searchquery="SELECT * from Users where user_name=%s or user_email=%s"
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        except Exception as e:
            error= f"Error: {e.args[1]}"
            return render_template('users.html', rows=result, data=error)
        return  render_template('users.html', rows=searchresult)
    elif "Return" in request.form:
        return redirect('/users')

  
#display update form and process any updates, using the same function
@bopify.route('/update_users/<int:user_ID>', methods=['POST','GET'])
def update_users(user_ID):
    print('In the function')
    db_connection = connect_to_database(host,user,passwd,db)
    #display existing data
    if request.method == 'GET':
        print('The GET request')
        users_query = 'SELECT user_ID, user_name, user_email from Users WHERE user_ID = %s'  % (user_ID)
        users_result = execute_query(db_connection, users_query).fetchone()

        if users_result == None:
            return "No such person found!"

        print('Returning')
        return render_template('users_update.html', user = users_result)
    elif request.method == 'POST':
        print('The POST request')
        user_ID = request.form['user_ID']
        user_name = request.form['user_name']
        user_email = request.form['user_email']

        query = "UPDATE Users SET user_name = %s, user_email = %s WHERE user_ID = %s"
        data = (user_name, user_email, user_ID)
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        return redirect('/users')

@bopify.route('/delete_users/<int:user_ID>')
def delete_users(user_ID):
    '''deletes a user with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    query = "DELETE FROM Users WHERE user_ID = %s"
    data = (user_ID,)

    execute_query(db_connection, query, data)
    return redirect('/users')



#################### END USERS ######################

############# PLAYLIST FUNCTIONALITY ################



@bopify.route('/playlists')
def playlists():


    print("Fetching and rendering playlists web page")
    db_connection = connect_to_database(host,user,passwd,db)
    query = "SELECT playlist_ID, playlist_name, user_ID from Playlists;"
    result = execute_query(db_connection, query).fetchall()
    usersquery = "SELECT user_ID, user_name, user_email from Users;"
    usersresult = execute_query(db_connection, usersquery).fetchall()
    print(result)
    print(usersresult)


    return render_template('playlists.html', rows=result,users=usersresult)


@bopify.route('/playlists_functionality/', methods=['GET', 'POST'])
def playlists_functionality():
    
    db_connection = connect_to_database(host,user,passwd,db)

    playlistsquery = "SELECT playlist_name, user_ID, playlist_ID from Playlists;"
    playlistsresult = execute_query(db_connection, playlistsquery).fetchall()
    print(playlistsresult)

    usersquery = "SELECT user_ID, user_name from Users;"
    usersresult = execute_query(db_connection, usersquery).fetchall()
    print(usersresult)


    if "Submit" in request.form:
        print("Add new playlists!")
        playlist_name = request.form['playlist_name']
        user_ID = request.form['user_ID']

        insertquery = 'INSERT INTO Playlists (playlist_name, user_ID) VALUES (%s,%s)'
        insertdata = [playlist_name, user_ID]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': 
                insertdata[index] = None
            index += 1
        try:
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            error = f"Error: {e.args[1]}" 
            return  render_template('playlists.html', rows=playlistsresult, users=usersresult, data=error)


                # print out a message to let the user know a cashier was added
        insertresult = f"Playlist Added: {playlist_name}"

        # query to get new data
        playlistsquery = "SELECT playlist_name, user_ID, playlist_ID from Playlists;"
        playlistsresult = execute_query(db_connection, playlistsquery).fetchall()
        print(playlistsresult)

        usersquery = "SELECT user_ID, user_name from Users;"
        usersresult = execute_query(db_connection, usersquery).fetchall()

        return  render_template('playlists.html', rows=playlistsresult, users=usersresult, insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    elif "Search" in request.form:
        playlist_name = request.form['playlist_name']

        searchdata=(playlist_name)
        searchquery="SELECT * from Playlists where playlist_name=%s"
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('playlists.html', rows=playlistsresult, users=usersresult, data=error)
        return  render_template('playlists.html', rows=searchresult, users=usersresult)
    elif "Return" in request.form:
        return redirect('/playlists')

        

#display update form and process any updates, using the same function
@bopify.route('/update_playlists/<int:id>', methods=['POST','GET'])
def update_playlists(id):
    print('In the function')
    db_connection = connect_to_database(host,user,passwd,db)
    #display existing data
    if request.method == 'GET':
        print('The GET request')
        playlists_query = 'SELECT playlist_name, user_ID, playlist_ID from Playlists WHERE playlist_ID = %s;'  % (id)
        playlists_result = execute_query(db_connection, playlists_query).fetchone()
        print(playlists_result)

        if playlists_result == None:
            return "No such playlists found!"
        usersquery = "SELECT user_ID, user_name from Users;"
        usersresult = execute_query(db_connection, usersquery).fetchall()
        print(usersresult)
        print('Returning')
        return render_template('playlists_update.html',playlist = playlists_result, users = usersresult)
    elif request.method == 'POST':
        print('The POST request')
        playlist_name = request.form['playlist_name']
        user_ID = request.form['user_ID']
        playlist_ID = request.form['playlist_ID']
        data = (playlist_name, user_ID, playlist_ID)
        print(data)
        query = "UPDATE Playlists SET playlist_name = %s, user_ID = %s WHERE playlist_ID = %s;"
    
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        return redirect('/playlists')

@bopify.route('/delete_playlists/<int:id>')
def delete_playlists(id):
    '''deletes a playlist with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    query = "DELETE FROM Playlists WHERE playlist_ID = %s"
    data = (id,)

    result = execute_query(db_connection, query, data)
    return redirect('/playlists')


################## END PLAYLISTS ####################

######### PLAYLISTINSONGS FUNCTIONALITY #############

############# END PLAYLISTSINSONGS ##################



if __name__ == '__main__':
    bopify.run(host='0.0.0.0', port=9119, debug=True)