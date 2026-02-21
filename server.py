from bottle import get, post, request, response, run
import sqlite3
from urllib.parse import quote, unquote

HOST = 'localhost'
PORT = 7007

db = sqlite3.connect("movies.sqlite")
db.set_trace_callback(print)

@get('/')
def get_index():
    response.status = 200
    return 'Use a more interesting endpoint such as `/movies` or `/users/name/tickets`'

@get('/ping')
def get_ping():
    response.status = 200
    return 'pong'

@get('/movies')
def get_movies():
    c = db.cursor()
    c.execute(
        '''
        SELECT imdb, title, year
        FROM movies
        '''
    )
    found = [{'imdbKey': imdb,
              'title': title,
              'year': year} for imdb,title,year in c]
    response = 200 if len(found)>0 else 404
    return {'data': found}

@get('/movies/<imdb>')
def get_movie(imdb):
    c = db.cursor()
    c.execute(
        '''
        SELECT  imdb, title, year
        FROM    movies
        WHERE   imdb = ?
        ''',
        [imdb]
    )
    found = [{'imdbKey': imdb,
              'title': title,
              'year': year} for imdb,title,year in c]
    response = 200 if len(found)>0 else 404
    return {'data': found}


@post('/movies')
def post_movie():
    movie = request.json
    c = db.cursor()
    c.execute(
        '''
        INSERT
        INTO movies(imdb, title, year)
        VALUES (?,?,?)
        RETURNING imdb
        ''',
        [movie['imdbKey'], movie['title'], movie['year']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return 'Could not create movie'
    else:
        db.commit()
        imdb, = found
        response = 201
        return f'/movies/{imdb}'

@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute(
        '''
        WITH sold_tickets AS (
            SELECT      s_id, count() as 'sold'
            FROM        tickets
            GROUP BY    s_id
        )
        SELECT s_id, date, time, title, year, t_name, capacity - ifnull(sold,0) as 'remaining_seats'
        FROM screenings
            JOIN theatres USING(t_name)
            JOIN movies USING(imdb)
            LEFT JOIN sold_tickets USING(s_id)    
        '''
    )
    found = [{'performanceId': s_id,
              'date': date,
              'startTime': time,
              'title': title,
              'year': year,
              'theater': t_name,
              'remainingSeats': remaining_seats} for s_id, date, time, title, year, t_name, remaining_seats in c]
    response.status = 200 if len(found)>0 else 404
    return {'data': found}

@post('/performances')
def post_performance():
    performance = request.json
    c = db.cursor()
    c.execute(
        '''
        INSERT
        INTO screenings(imdb, date, time, t_name)
        VALUES (?,?,?,?)
        RETURNING s_id
        ''',
        [performance['imdbKey'], performance['date'], performance['time'], performance['theater']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return 'Could not create performance'
    else:
        db.commit()
        s_id, = found
        response = 201
        return f'/performances/{s_id}'

@get('/tickets')
def get_tickets():
    c = db.cursor()
    c.execute(
        '''
        SELECT date, time, title, year, t_name
        FROM tickets
            JOIN screenings USING(s_id)
            JOIN movies USING(imdb)
        '''
    )
    found = [{'date': date,
              'startTime': time,
              'theatre': t_name,
              'title': title,
              'year': year
              } for date, time, title, year, t_name in c]
    response.status = 200 if len(found)>0 else 404
    return {'data': found}

@post('/tickets')
def post_ticket():
    ticket = request.json
    c = db.cursor()
    c.execute('''BEGIN TRANSACTION''')
    c.execute(
        '''
        INSERT
        INTO tickets    (s_id, u_name)
        SELECT          ?,?
        RETURNING       id
        ''',
        [ticket['performanceId'], ticket['username']]
    )
    found = c.fetchone()
    print(found)

    c.execute(
        '''
        SELECT capacity
        FROM    screenings
            JOIN theatres USING(t_name)
        WHERE   s_id = ?
        ''',
        [ticket['performanceId']]
    )
    capacity = c.fetchone()[0]
    
    c.execute(
        '''
        SELECT count()
        FROM    tickets
        WHERE   s_id = ?
        ''',
        [ticket['performanceId']]
    )
    sold_tickets = c.fetchone()[0]
    
    print(f'sold: {sold_tickets} and capacity: {capacity}')

    if not found or sold_tickets>capacity:
        response.status = 400
        db.rollback()
        return 'No tickets left'
    else:
        db.commit()
        response.status = 201
        id, = found
        print(id)
        return f'/tickets/{id}'

@get('/users')
def get_users():
    c = db.cursor()
    c.execute(
        '''
        SELECT u_name, full_name, pwd
        FROM customers
        '''
    )
    found = [{'username': u_name,
              'fullName':full_name,
              'pwd':pwd,
              } for u_name, full_name, pwd in c]
    response = 200 if len(found)>0 else 404
    return {'data': found}

@get('/users/<u_name>/tickets')
def get_tickets_per_user(u_name):
    c = db.cursor()
    c.execute(
        '''
        SELECT  date, time, t_name, title, year, count() as nbr_tickets
        FROM    tickets
            JOIN    screenings  USING (s_id)
            JOIN    movies      USING (imdb)
            JOIN    customers   USING (u_name)
        WHERE   u_name = ?
        GROUP BY    s_id
        ''',
        [u_name]
    )
    found = [{'date': date,
              'startTime': time,
              'theater':t_name,
              'title':title,
              'year':year,
              'nbrOfTickets':nbr_tickets} for date, time, t_name, title, year, nbr_tickets in c]
    response.status = 200 if len(found)>0 else 404
    return {'data':found}

@post('/users')
def post_user():
    user = request.json
    c = db.cursor()
    c.execute(
        '''
        INSERT
        INTO customers(u_name, full_name, pwd)
        VALUES (?,?,?)
        RETURNING u_name
        ''',
        [user['username'], user['fullName'], user['pwd']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return 'Could not create user'
    else:
        db.commit()
        u_name, = found
        response = 201
        return f'/users/{u_name}'


@post('/reset')
def reset():
    c = db.cursor()
    with open('lab3.sql', 'r') as schema:
        content = schema.read()
        c.executescript(content)
    db.commit()

run(host=HOST, port=PORT)