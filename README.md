# What to expect 
This project allows accessing and adding movies, users and tickets into a database by using [JSON](https://www.json.org/json-en.html) over [HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP). There are also theaters and screenings/performences of the of the movies stored.

# Usage
The server is run via the `server.py` file and then opens on <http://localhost:7007> by default. Both host and port can be changed at the top of the `server.py` file.

# Endpoints
The enpoints availiable include, but are not limited to:
- GET   /
- GET   /ping
- GET   /movies
- GET   /movies/<imdb>
- POST  /movies
- GET   /performances
- POST  /performances
- GET   /tickets
- GET   /users
- GET   /users/<username>/tickets
- POST  /reset
