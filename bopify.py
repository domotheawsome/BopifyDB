

from importlib.util import resolve_name
import os
import MySQLdb
from dotenv import load_dotenv
from flask import Flask, request, render_template,redirect
import configparser



##### DATABASE CONFIGURATION ######

### This is hardcoded for my database (Ariel), you can 
### change it to connect to your database. 


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
    connects to the database, mySQLDB and returns a database object
    takes in configuration details above
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

### set up initial database connection
db_connection = connect_to_database(host,user,passwd,db)
### declare dict cursor
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


################### HOME PAGE #######################

@bopify.route('/')
def index():
    ''' simply rendering index.html'''
    return render_template('index.html')


############ ARTIST FUNCTIONALITY ###################

'''
    When you navigate to Artists, it will query the artists database 
    for the current artist data and renders it in the artists.html 
    page. This implements the READ functionality by reading 
    in all of the data using SELECT.
    
    Artists shares a one to many relationship with both Albums and Songs. Artists does not inherit foriegn keys. 

'''

### routing to artists
@bopify.route('/artists')
def artists():
    print("Fetching and rendering artists web page")
    # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)
    # declaring the SELECT query
    query = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    # getting the results of the query/columns of artists
    result = execute_query(db_connection, query).fetchall()
    print(result)

    # rendering the data in artists.html
    return render_template('artists.html', rows=result)

'''
    once the user clicks on a form button, the page is re-routed
    to perform the corresponding functionality. this handles
    requests for CREATE, SEARCH, and DELETE. 

'''

### rerouting to perform artist functionality
@bopify.route('/artists_functionality/', methods=['GET', 'POST'])
def artists_functionality():
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # reading in all columns in the Artists table
    artistsquery = "SELECT artist_fname, artist_lname, artist_ID from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)

    ### this handles the INSERT functionality
    if "Submit" in request.form:
        print("Add new Artists!")

        
        # getting text submitted by the user
        artist_fname = request.form['artist_fname']
        artist_lname = request.form['artist_lname']

        # declare the Artist INSERT query using data from above
        insertquery = 'INSERT INTO Artists (artist_fname, artist_lname) VALUES (%s,%s)'
        
        # data to be entered into the insert query
        insertdata = [artist_fname, artist_lname]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            # perform the query
            execute_query(db_connection, insertquery, insertdata)

        except Exception as e:
            # if the query throws an error, print to the screen
            error = f"Error: {e.args[1]}" 
            return  render_template('artists.html', rows=result, data=error)


        # print out a message to let the user know an artist was added
        insertresult = f"Artist Added: {artist_fname} {artist_lname}"

        # query again to get Artist data after the insert query
        query = "SELECT artist_fname, artist_lname, artist_ID from Artists;"

        result = execute_query(db_connection, query)

        # render the new data in the page
        return  render_template('artists.html', rows=result,  insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    ### performs SEARCH functionality
    elif "Search" in request.form:
        # getting text submitted by the user
        artist_fname = request.form['artist_fname']
        artist_lname = request.form['artist_lname']

        # save data from above
        searchdata=(artist_fname, artist_lname)

        # declare the Artist SEARCH query, we use the OR keyword
        # to allow user to search within either column
        searchquery="SELECT * from Artists where artist_fname=%s or artist_lname=%s"

        try:
            # try the search query
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()

        #if the query throws an error, print to the screen
        except Exception as e:
            error= f"Error: {e.args[1]}"
            return render_template('artists.html', rows=result, data=error)

        # render Artists with the search result
        return  render_template('artists.html', rows=searchresult)

    ### returns from SEARCH
    elif "Return" in request.form:
        # once SEARCH is complete, reroute to Artists page to view all data 
        return redirect('/artists')

'''
    once the user clicks on an update button, the page is re-routed
    to display the update form, the corresponding id is used to
    perform the UPDATE query. once complete, it re-routes/returns to the artist page with the updated information. 

'''
# display update form and process any updates, return back to /artists
# when complete. 
@bopify.route('/update_artists/<int:artist_ID>', methods=['POST','GET'])
def update_artists(artist_ID):

    print('In the function')
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # render the form with existing data
    if request.method == 'GET':
        print('The GET request')

        # getting artist data for the ID selected, querying using
        # the WHERE keyword 
        artists_query = 'SELECT artist_ID, artist_fname, artist_lname from Artists WHERE artist_ID = %s'  % (artist_ID)
        artists_result = execute_query(db_connection, artists_query).fetchone()

        if artists_result == None:
            return "No such person found!"

        # rendering update form template, sending current data for ID
        # to the form
        return render_template('artists_update.html', artist = artists_result)

    elif request.method == 'POST':
        print('The POST request')

        # getting all of the user inputted data
        artist_ID = request.form['artist_ID']
        artist_fname = request.form['artist_fname']
        artist_lname = request.form['artist_lname']

        # declaring the UPDATE query for the specific ID
        query = "UPDATE Artists SET artist_fname = %s, artist_lname = %s WHERE artist_ID = %s"

        # storing the user inputted data
        data = (artist_fname, artist_lname, artist_ID)

        # performing the UPDATE query. prints the number
        # of rows updated to the server
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        # returning back to artists. artists will then render
        # with the current (updated) database.
        return redirect('/artists')



'''
    once the user clicks on the delete button in the table, the
    corresponding id is used to perform the DELETE functionality/
    query. After the operation is complete, it returns to the 
    artist page with the updated information. 

'''

@bopify.route('/delete_artists/<int:artist_ID>')
def delete_artists(artist_ID):
    '''deletes an artist with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    # declaring the query, using the WHERE keyword
    query = "DELETE FROM Artists WHERE artist_ID = %s"
    data = (artist_ID,)

    # performing query
    execute_query(db_connection, query, data)
    
    # redirecting back to artists once complete
    return redirect('/artists')


#################### END ARTISTS #####################


################ ALBUM FUNCTIONALITY #################

'''
    When you navigate to Albums, it will query the albums database 
    for the current albums data and renders it in the albums.html 
    page. This implements the READ functionality by reading 
    in all of the data using SELECT.
    
    Albums shares 0 or many to one relationship with artists, and a 
    one to many relationship with both Songs. Albums inherits the 
    foreign key for Artists (artist_ID) per this many:one relationship. 
'''


@bopify.route('/albums')
def albums():

    # printing out to the server that we entered the albums page
    print("Fetching and rendering albums web page")

    # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # declaring the SELECT query
    query = "SELECT album_name, album_genre, artist_ID, album_ID from Albums;"

    # getting the results of the query/columns of albums
    result = execute_query(db_connection, query).fetchall()

    # declaring the SELECT query for artists. we need the artist information
    # per the relationship between artists and albums. 
    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()

    # rendering the data in albums.html
    return render_template('albums.html', rows=result,artists=artistsresult)


'''
    once the user clicks on a form button, the page is re-routed
    to perform the corresponding functionality. this handles
    requests for CREATE, SEARCH, and DELETE. 

'''

@bopify.route('/albums_functionality/', methods=['GET', 'POST'])
def albums_functionality():
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # reading in all columns in the Albums table
    albumsquery = "SELECT album_name, album_genre, artist_ID, album_ID from Albums;"
    albumsresult = execute_query(db_connection, albumsquery).fetchall()
    print(albumsresult)

    # reading in the data for artists. we need the artist information
    # per the relationship between artists and albums. 
    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)

    ### this handles the INSERT functionality
    if "Submit" in request.form:
        print("Add new albums!")

         # getting text submitted by the user
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']
        artist_ID = request.form['artist_ID']

        # declare the Albums INSERT query using data from above
        insertquery = 'INSERT INTO Albums (album_name, album_genre, artist_ID) VALUES (%s,%s,%s)'
        insertdata = [album_name, album_genre, artist_ID]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': insertdata[index] = None
            index += 1
        try:
            # perform the query
            execute_query(db_connection, insertquery, insertdata)

        except Exception as e:
            
            # if the query throws an error, print to the screen
            error = f"Error: {e.args}" 
            return  render_template('albums.html', rows=albumsresult, artists=artistsresult, data=error)


        # print out a message to let the user know an album was added
        insertresult = f"Album Added: {album_name} {album_genre}"

        # query again to get Album and Artist data after the insert query
        albumsquery = "SELECT album_name, album_genre, artist_ID, album_ID from Albums;"
        albumsresult = execute_query(db_connection, albumsquery).fetchall()
       
        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()

        # render the new data in the page
        return  render_template('albums.html', rows=albumsresult, artists=artistsresult, insertresult=insertresult)

    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass

    ### performs SEARCH functionality
    elif "Search" in request.form:

        # getting text submitted by the user
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']

        # save data from above
        searchdata=(album_name, album_genre)

         # declare the Albums SEARCH query, we use the OR keyword
        # to allow user to search within either column
        searchquery="SELECT * from Albums where album_name=%s or album_genre=%s "
        try:

            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()

        #if the query throws an error, print to the screen
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('albums.html', rows=albumsresult, artists=artistsresult, data=error)

        # render Albums with the search result
        return  render_template('albums.html', rows=searchresult, artists=artistsresult)

     ### returns from SEARCH
    elif "Return" in request.form:
        # once SEARCH is complete, reroute to Albums page to view entire database 
        return redirect('/albums')

        

# display update form and process any updates, return back to /albums
# when complete. 
@bopify.route('/update_albums/<int:id>', methods=['POST','GET'])
def update_albums(id):
    print('In the function')
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)
    # render the form with existing data
    if request.method == 'GET':
        print('The GET request')
        # getting Album data for the ID selected, querying using
        # the WHERE keyword 
        albums_query = 'SELECT album_name, album_genre, artist_ID, album_ID from Albums WHERE album_ID = %s'  % (id)
        albums_result = execute_query(db_connection, albums_query).fetchone()

        if albums_result == None:
            return "No such album found!"

        # get appropriate artist data to populate foreign key dropdown 
        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()

        # rendering update form template, sending current data for ID
        # to the form
        return render_template('albums_update.html', artists = artistsresult, album = albums_result)
    elif request.method == 'POST':
        print('The POST request')

         # getting all of the user inputted data
        album_ID = request.form['album_ID']
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']
        artist_ID = request.form['artist_ID']
        
        data = (album_name, album_genre, artist_ID, album_ID)

        # declaring the UPDATE query for the specific ID
        query = "UPDATE Albums SET album_name = %s, album_genre = %s, artist_ID = %s WHERE album_ID = %s"
    
        # performing the UPDATE query. prints the number
        # of rows updated to the server
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        # returning back to albums. albums will then render
        # with the current (updated) database.
        return redirect('/albums')


'''
    once the user clicks on the delete button in the table, the
    corresponding id is used to perform the DELETE functionality/
    query. After the operation is complete, it returns to the 
    artist page with the updated information. 

'''

@bopify.route('/delete_albums/<int:id>')
def delete_albums(id):
    '''deletes an album with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)

    # declaring the query, using the WHERE keyword
    query = "DELETE FROM Albums WHERE album_ID = %s"
    data = (id,)

    # performing query
    result = execute_query(db_connection, query, data)

    # redirecting back to albums once complete
    return redirect('/albums')


#################### END ALBUMS ######################


################ SONGS FUNCTIONALITY #################

'''
    When you navigate to Songs, it will query the Songs database 
    for the current Song data and renders it in the Songs.html 
    page. This implements the READ functionality by reading 
    in all of the data using SELECT.
    
    Songs shares a many to one relationship with albums, and a zero or
    many to one relationship with songs. it also shares a one to many
    relationship with PlaylistsSongs, which is the many:many relationship
    in our schema and connects to Playlists. It inherits two foreign keys from Albums and Playlists to satisfy these relationships.  
'''


@bopify.route('/songs')
def songs():
    print("Fetching and rendering songs web page")

     # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # declaring the SELECT query
    query = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs;"

     # getting the results of the query/columns of songs
    result = execute_query(db_connection, query).fetchall()

    # declaring the SELECT query for artists. we need the artist information
    # per the relationship between songs and artists.
    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()
    print(artistsresult)

    # declaring the SELECT query for albums. we need the album information
    # per the relationship between songs and albums.
    albumsquery = "SELECT album_ID, album_name from Albums;"
    albumsresult = execute_query(db_connection, albumsquery).fetchall()
    print(albumsresult)

    # rendering the data in songs.html
    return render_template('songs.html', rows=result, albums=albumsresult, artists=artistsresult)


'''
    once the user clicks on a form button, the page is re-routed
    to perform the corresponding functionality. this handles
    requests for CREATE, SEARCH, and DELETE. 

'''

@bopify.route('/songs_functionality/', methods=['GET', 'POST'])
def songs_functionality():
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # reading in all columns in the Songs table
    songsquery = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs;"

    # saving the result
    songsresult = execute_query(db_connection, songsquery).fetchall()

    # reading in the data for Albums and Artists. we need the artist/album 
    # information per the relationship between Songs and Artists/Albums.
    albumsquery = "SELECT album_name, album_ID from Albums;"
    albumsresult = execute_query(db_connection, albumsquery).fetchall()

    artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
    artistsresult = execute_query(db_connection, artistsquery).fetchall()

    ### this handles the INSERT functionality
    if "Submit" in request.form:
        print("Add new songs!")
        # getting text submitted by the user
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
            # perform the query
            execute_query(db_connection, insertquery, insertdata)

        except Exception as e:
            # if the query throws an error, print to the screen
            error = f"Error: {e.args}" 
            return  render_template('songs.html', rows=songsresult, albums=albumsresult, artists=artistsresult, data=error)

        insertresult = f"Song Added: {song_name} {song_genre}"

        # query to get new data after INSERT
        songsquery = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs;"
        songsresult = execute_query(db_connection, songsquery).fetchall()
        print(songsresult)

        # query again for Artists and Albums
        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()
        print(artistsresult)

        albumsquery = "SELECT album_name, album_ID from Albums;"
        albumsresult = execute_query(db_connection, albumsquery).fetchall()
        print(albumsresult)
        # render the new SELECT data in the page
        return render_template('songs.html', rows=songsresult,albums=albumsresult, artists=artistsresult, insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
    ### performs SEARCH functionality
    elif "Search" in request.form:
        # getting text submitted by the user
        song_name = request.form['song_name']
        song_genre = request.form['song_genre']

        searchdata=(song_name, song_genre)

        # declare the Songs SEARCH query, we use the OR keyword
        # to allow user to search within either column
        searchquery="SELECT * from Songs where song_name=%s or song_genre=%s "
       
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
        
        #if the query throws an error, print to the screen
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('songs.html', rows=songsresult, albums=albumsresult, artists=artistsresult, data=error)
        
        # render Songs with the search result
        return  render_template('songs.html', rows=searchresult, albums=albumsresult, artists=artistsresult)
 
    elif "Return" in request.form:

        # once SEARCH is complete, reroute to Songs page to view entire database 
        return redirect('/songs')

        

# display update form and process any updates, return back to /songs
# when complete. 
@bopify.route('/update_songs/<int:id>', methods=['POST','GET'])
def update_songs(id):
    print('In the function')
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # render the form with existing data
    if request.method == 'GET':
        print('The GET request')

        # getting Song data for the ID selected, querying using
        # the WHERE keyword
        songsquery = "SELECT song_name, song_genre, artist_ID, album_ID, song_ID from Songs WHERE song_ID = %s;" % (id)
        songsresult = execute_query(db_connection, songsquery).fetchone()
        print(songsresult)

        if songsresult == None:
            return "No such song found!"
        
         # get appropriate album and artist data to populate foreign key dropdown 
        albums_query = 'SELECT album_name, album_ID from Albums;'
        albums_result = execute_query(db_connection, albums_query).fetchall()

        artistsquery = "SELECT artist_ID, artist_fname, artist_lname from Artists;"
        artistsresult = execute_query(db_connection, artistsquery).fetchall()

         # rendering update form template, sending current data for ID
        # to the form
        return render_template('songs_update.html', song = songsresult, artists = artistsresult, albums = albums_result)

    ### after the user hits submit on the update form
    elif request.method == 'POST':
        print('The POST request')
        # getting all of the user inputted data
        song_ID = request.form['song_ID']
        song_name = request.form['song_name']
        song_genre = request.form['song_genre']
        album_ID = request.form['album_ID']
        artist_ID = request.form['artist_ID']

  
        data = (song_name, song_genre, album_ID, artist_ID, song_ID)
        
        query = "UPDATE Songs SET song_name = %s, song_genre = %s, album_ID = %s, artist_ID = %s WHERE song_ID = %s"
        
        # performing the UPDATE query. prints the number
        # of rows updated to the server
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        # returning back to songs. songs will then render
        # with the current (updated) database.
        return redirect('/songs')

'''
    once the user clicks on the delete button in the table, the
    corresponding id is used to perform the DELETE functionality/
    query. After the operation is complete, it returns to the 
    artist page with the updated information. 

'''

@bopify.route('/delete_songs/<int:id>')
def delete_songs(id):
    '''deletes a song with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
     # declaring the query, using the WHERE keyword
    query = "DELETE FROM Songs WHERE song_ID = %s"
     # storing ID to use in query
    data = (id,)
     # performing query
    result = execute_query(db_connection, query, data)
    # redirecting back to songs once complete
    return redirect('/songs')



#################### END SONGS ######################

############### USER FUNCTIONALITY ##################


'''
    When you navigate to Users, it will query the Users database 
    for the current Users data and render it in the users.html 
    page. This implements the READ functionality by reading 
    in all of the data using SELECT.
    
    Users shares a one to zero or many relationship with Playlists.
    It inherits no foriegn keys. 
'''



@bopify.route('/users')
def users():
    print("Fetching and rendering artists web page")
    # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)
    # declaring the SELECT query
    query = "SELECT user_ID, user_name, user_email from Users;"
    result = execute_query(db_connection, query).fetchall()
    print(result)

    # rendering the data in users.html
    return render_template('users.html', rows=result)

'''
    once the user clicks on a form button, the page is re-routed
    to perform the corresponding functionality. this handles
    requests for CREATE, SEARCH, and DELETE. 

'''

@bopify.route('/users_functionality/', methods=['GET', 'POST'])
def users_functionality():
     # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)

     # reading in all columns in the Users table
    usersquery = "SELECT artist_fname, artist_lname, artist_ID from Artists;"
    usersresult = execute_query(db_connection, usersquery).fetchall()
    print(usersresult)


    ### this handles the INSERT functionality
    if "Submit" in request.form:
        print("Add new Users!")

        # getting text submitted by the user
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
            # perform the query
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            # if the query throws an error, print to the screen
            error = f"Error: {e.args[1]}" 
            return  render_template('users.html', rows=result, data=error)


        # print out a message to let the user know a user was added
        insertresult = f"User Added: {user_name} {user_email}"

        # query to get new data after INSERT
        query = "SELECT user_name, user_email, user_ID from Users;"
        result = execute_query(db_connection, query)

        # render the new SELECT data in the page
        return  render_template('users.html', rows=result,  insertresult=insertresult)
    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass
     ### performs SEARCH functionality
    elif "Search" in request.form:
        # getting text submitted by the user
        user_name = request.form['user_name']
        user_email = request.form['user_email']
    
        searchdata=(user_name, user_email)
         # declare the Users SEARCH query, we use the OR keyword
        # to allow user to search within either column
        searchquery="SELECT * from Users where user_name=%s or user_email=%s"
        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()

        #if the query throws an error, print to the screen
        except Exception as e:
            error= f"Error: {e.args[1]}"
            return render_template('users.html', rows=result, data=error)
        # render Users with the search result
        return  render_template('users.html', rows=searchresult)
    elif "Return" in request.form:
        # once SEARCH is complete, reroute to Users page to view entire database 
        return redirect('/users')

  
#display update form and process any updates, using the same function
@bopify.route('/update_users/<int:user_ID>', methods=['POST','GET'])
def update_users(user_ID):
    print('In the function')
     # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)
     # render the form with existing data
    if request.method == 'GET':
        print('The GET request')
        # getting User data for the ID selected, querying using
        # the WHERE keyword
        users_query = 'SELECT user_ID, user_name, user_email from Users WHERE user_ID = %s'  % (user_ID)
        users_result = execute_query(db_connection, users_query).fetchone()

        if users_result == None:
            return "No such person found!"

        # rendering update form template, sending current data for ID
        # to the form
        return render_template('users_update.html', user = users_result)

     ### after the user hits submit on the update form
    elif request.method == 'POST':
        print('The POST request')

         # getting all of the user inputted data
        user_ID = request.form['user_ID']
        user_name = request.form['user_name']
        user_email = request.form['user_email']

        query = "UPDATE Users SET user_name = %s, user_email = %s WHERE user_ID = %s"
        data = (user_name, user_email, user_ID)

        # performing the UPDATE query. prints the number
        # of rows updated to the server
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        # returning back to songs. songs will then render
        # with the current (updated) database.
        return redirect('/users')

'''
    once the user clicks on the delete button in the table, the
    corresponding id is used to perform the DELETE functionality/
    query. After the operation is complete, it returns to the 
    artist page with the updated information. 

'''


@bopify.route('/delete_users/<int:user_ID>')
def delete_users(user_ID):
    '''deletes a user with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
     # declaring the query, using the WHERE keyword
    query = "DELETE FROM Users WHERE user_ID = %s"
     # storing ID to use in query
    data = (user_ID,)
    # performing query
    execute_query(db_connection, query, data)
    # redirecting back to users once complete
    return redirect('/users')



#################### END USERS ######################

############# PLAYLIST FUNCTIONALITY ################

'''
    When you navigate to Playlists, it will query the Playlsits database 
    for the current Playlists and render it in the playlists.html 
    page. This implements the READ functionality by reading 
    in all of the data using SELECT.
    
   Plyalists shares a one to many relationship with PlaylistsSongs (this
   is the M:M relationship implementation) and a 0 or many to one 
   relationship with users. It inherits one foreign key from Users.
'''

@bopify.route('/playlists')
def playlists():
    print("Fetching and rendering playlists web page")
     # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)
    
    # declaring the SELECT query
    query = "SELECT playlist_ID, playlist_name, user_ID from Playlists;"
    result = execute_query(db_connection, query).fetchall()
    
    # declaring the SELECT query for users. we need the user information
    # per the relationship between playlists and users.
    usersquery = "SELECT user_ID, user_name, user_email from Users;"
    usersresult = execute_query(db_connection, usersquery).fetchall()

    # rendering the data in playlists.html
    return render_template('playlists.html', rows=result,users=usersresult)

'''
    once the user clicks on a form button, the page is re-routed
    to perform the corresponding functionality. this handles
    requests for CREATE, SEARCH, and DELETE. 

'''

@bopify.route('/playlists_functionality/', methods=['GET', 'POST'])
def playlists_functionality():
     # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

     # reading in all columns in the Playlists table
    playlistsquery = "SELECT playlist_name, user_ID, playlist_ID from Playlists;"
    # saving the result
    playlistsresult = execute_query(db_connection, playlistsquery).fetchall()

    # declaring the SELECT query for users. we need the user information
    # per the relationship between playlists and users.
    usersquery = "SELECT user_ID, user_name from Users;"
    usersresult = execute_query(db_connection, usersquery).fetchall()

    ### this handles the INSERT functionality
    if "Submit" in request.form:
        print("Add new playlists!")
        # getting text submitted by the user
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
            # perform the query
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            # if the query throws an error, print to the screen
            error = f"Error: {e.args[1]}" 
            return  render_template('playlists.html', rows=playlistsresult, users=usersresult, data=error)


        # print out a message to let the user know a playlist was added
        insertresult = f"Playlist Added: {playlist_name}"

        # query to get new data after INSERT
        playlistsquery = "SELECT playlist_name, user_ID, playlist_ID from Playlists;"
        playlistsresult = execute_query(db_connection, playlistsquery).fetchall()
        print(playlistsresult)

        usersquery = "SELECT user_ID, user_name from Users;"
        usersresult = execute_query(db_connection, usersquery).fetchall()

         # render the new SELECT data in the page
        return  render_template('playlists.html', rows=playlistsresult, users=usersresult, insertresult=insertresult)

    elif "Update" in request.form:
        pass
    elif "Delete" in request.form:
        pass

    ### performs SEARCH functionality
    elif "Search" in request.form:
        # getting text submitted by the user
        playlist_name = request.form['playlist_name']

        searchdata=(playlist_name)
        # declare the Playlists SEARCH query, we use the OR keyword
        # to allow user to search within either column
        searchquery="SELECT * from Playlists where playlist_name=%s"

        try:
            searchresult=execute_query(db_connection, searchquery, searchdata).fetchall()
         #if the query throws an error, print to the screen
        except Exception as e:
            error=f"Error: {e.args[1]}"
            return render_template('playlists.html', rows=playlistsresult, users=usersresult, data=error)

        # render Playlists with the search result
        return  render_template('playlists.html', rows=searchresult, users=usersresult)
    elif "Return" in request.form:
        # once SEARCH is complete, reroute to Playlists page to view entire database 
        return redirect('/playlists')

        

# display update form and process any updates, return back to /playlists
# when complete. 
@bopify.route('/update_playlists/<int:id>', methods=['POST','GET'])
def update_playlists(id):
    print('In the function')
     # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)
     # render the form with existing data

    if request.method == 'GET':
        print('The GET request')
        # getting Playlist data for the ID selected, querying using
        # the WHERE keyword
        playlists_query = 'SELECT playlist_name, user_ID, playlist_ID from Playlists WHERE playlist_ID = %s;'  % (id)
        playlists_result = execute_query(db_connection, playlists_query).fetchone()
        print(playlists_result)

        if playlists_result == None:
            return "No such playlists found!"

        # get appropriate user data to populate foreign key dropdown 
        usersquery = "SELECT user_ID, user_name from Users;"
        usersresult = execute_query(db_connection, usersquery).fetchall()
        print(usersresult)
        print('Returning')

        # rendering update form template, sending current data for ID
        # to the form
        return render_template('playlists_update.html',playlist = playlists_result, users = usersresult)

    ### after the user hits submit on the update form
    elif request.method == 'POST':
        print('The POST request')
        # getting all of the user inputted data
        playlist_name = request.form['playlist_name']
        user_ID = request.form['user_ID']
        playlist_ID = request.form['playlist_ID']
        data = (playlist_name, user_ID, playlist_ID)
        
        query = "UPDATE Playlists SET playlist_name = %s, user_ID = %s WHERE playlist_ID = %s;"
    
        # performing the UPDATE query. prints the number
        # of rows updated to the server
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated")

        # returning back to playlists. playlists will then render
        # with the current (updated) database.

        return redirect('/playlists')

'''
    once the user clicks on the delete button in the table, the
    corresponding id is used to perform the DELETE functionality/
    query. After the operation is complete, it returns to the 
    artist page with the updated information. 

'''

@bopify.route('/delete_playlists/<int:id>')
def delete_playlists(id):
    '''deletes a playlist with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
     # declaring the query, using the WHERE keyword
    query = "DELETE FROM Playlists WHERE playlist_ID = %s"
    data = (id,)
    # performing query
    result = execute_query(db_connection, query, data)
    # redirecting back to playlists once complete
    return redirect('/playlists')


################## END PLAYLISTS ####################

######### PLAYLISTSSONGS FUNCTIONALITY #############



'''
    When you navigate to PlaylistsSongs, it will query the PlaylistsinSongs database for the current data and render it in the PlaylistsSongs.html 
    page. This implements the READ functionality by reading 
    in all of the data using SELECT.
    
    PlaylistsSongs is comprised of two foreign keys and a unique primary key.
    Given it is a junction table between playlists and songs to create the
    m:m relationship these entities share, it will inherit their respective
    primary keys, playlist_ID and song_ID. 
'''


## for PlaylistsSongs, we only have to implement
## the insert and delete functionality.

## we do not have to implement update/search, which
## makes sense given its a junction table




@bopify.route('/PlaylistsSongs')
def PlaylistsSongs():

    print("Fetching and rendering playlists web page")
    # connecting to the database
    db_connection = connect_to_database(host,user,passwd,db)

    # declaring the SELECT query
    PlaylistsSongsquery = "SELECT playlist_ID, song_ID, playlistinsong_ID from PlaylistsInSong;"
    PlaylistsSongsresult = execute_query(db_connection, PlaylistsSongsquery).fetchall()
    print(PlaylistsSongsresult)

    # declaring the SELECT query for playlists and songs. we need this information
    # per the M:M relationship between playlists and songs.

    playlistsquery = "SELECT playlist_ID, playlist_name from Playlists;"
    playlistsresult = execute_query(db_connection, playlistsquery).fetchall()

    songsquery = "SELECT song_name, song_ID from Songs;"
    songsresult = execute_query(db_connection, songsquery).fetchall()

    # rendering the data in PlaylistsSongs.html
    return render_template('PlaylistsSongs.html', rows=PlaylistsSongsresult, songs=songsresult, playlists=playlistsresult)


'''
    once the user clicks on a form button, the page is re-routed
    to perform the corresponding functionality. this handles
    requests for CREATE and DELETE. 

'''

@bopify.route('/PlaylistsSongs_functionality/', methods=['GET', 'POST'])
def PlaylistsSongs_functionality():
    # connect to the database
    db_connection = connect_to_database(host,user,passwd,db)

     # reading in all columns in the PlaylistsSongs table
    PlaylistsSongsquery = "SELECT playlist_ID, song_ID, playlistinsong_ID from PlaylistsInSong;"

    # saving the result
    PlaylistsSongsresult = execute_query(db_connection, PlaylistsSongsquery).fetchall()

    # reading in the data for Playlists and Songs. we need the playlist/song 
    # information per the relationship between Playlists and Songs .
    playlistsquery = "SELECT playlist_ID, playlist_name from Playlists;"
    playlistsresult = execute_query(db_connection, playlistsquery).fetchall()

    songsquery = "SELECT song_name, song_ID from Songs;"
    songsresult = execute_query(db_connection, songsquery).fetchall()

    ### this handles the INSERT functionality
    if "Submit" in request.form:
        print("Add new playlists!")
        # getting text submitted by the user
        playlist_ID = request.form['playlist_ID']
        song_ID = request.form['song_ID']

        insertquery = 'INSERT INTO PlaylistsInSong (playlist_ID, song_ID) VALUES (%s,%s)'
        insertdata = [playlist_ID, song_ID]

        # check for null/empty data
        index = 0
        for data in insertdata:
            if data == '': 
                insertdata[index] = None
            index += 1
        try:
            # perform the query
            execute_query(db_connection, insertquery, insertdata)


        except Exception as e:
            # if the query throws an error, print to the screen
            error = f"Error: {e.args[1]}" 
            return  render_template('PlaylistsSongs.html', rows=PlaylistsSongsresult, songs=songsresult, playlists=playlistsresult, data=error)


        # print out a message to let the user know PlaylistSong was added
        insertresult = f"PlaylistSong Added: {playlist_ID} {song_ID}"

        # query to get new data after INSERT
        PlaylistsSongsquery = "SELECT playlist_ID, song_ID, playlistinsong_ID from PlaylistsInSong;"
        PlaylistsSongsresult = execute_query(db_connection, PlaylistsSongsquery).fetchall()
        print(PlaylistsSongsresult)

        # query again for Playlists and Songs
        playlistsquery = "SELECT playlist_ID, playlist_name from Playlists;"
        playlistsresult = execute_query(db_connection, playlistsquery).fetchall()

        songsquery = "SELECT song_name, song_ID from Songs;"
        songsresult = execute_query(db_connection, songsquery).fetchall()
        print(songsresult)
        print(playlistsresult)

        # render the new SELECT data in the page
        return render_template('PlaylistsSongs.html', rows=PlaylistsSongsresult, songs=songsresult, playlists=playlistsresult, insertresult=insertresult)

    elif "Delete" in request.form:
        pass

'''
    once the user clicks on the delete button in the table, the
    corresponding id is used to perform the DELETE functionality/
    query. After the operation is complete, it returns to the 
    artist page with the updated information. 

'''
        
@bopify.route('/delete_PlaylistsSongs/<int:id>')
def delete_PlaylistsSongs(id):
    '''deletes a PlaylistSong with the given id'''
    db_connection = connect_to_database(host,user,passwd,db)
    # declaring the query, using the WHERE keyword
    query = "DELETE FROM PlaylistsInSong WHERE playlistinsong_ID = %s"
    data = (id,)
    # performing query
    result = execute_query(db_connection, query, data)
     # redirecting back to PlaylistsSongs once complete
    return redirect('/PlaylistsSongs')

############# END PLAYLISTSINSONGS ##################



if __name__ == '__main__':
    bopify.run(host='0.0.0.0', port=9120, debug=True)