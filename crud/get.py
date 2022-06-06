from fastapi import HTTPException
from sqlalchemy import select, text, desc

from db import engine
from models import Movies, movie_genres


## To GET all the movies

def getAllMovies(ASC=None, sort_by=None):
  # For Sorting
  if(ASC == True ):
    if( sort_by != None ):
      column = text(f"movies.{sort_by}")
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(column)
    else:
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(Movies.title)
  # Asc = false will used for sorting in descending order  
  elif( ASC == False ):
    if( sort_by != None ):
      column = text(f"movies.{sort_by}")
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(desc(column))
    else:
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(desc(Movies.title))
    print(stmt)
  else:
    stmt = select(Movies.id, Movies.title, Movies.rating)
    print(stmt)

  data = []
  conn = engine.connect()
  for row in conn.execute(stmt):
    data.append(row)
  conn.close()
  return {"status": "success", "length":len(data), "data":data}


# To get movie details of a single movie
def getMovie(movie_id):
  stmt = select(Movies).where(Movies.id == movie_id)
  conn = engine.connect()
  data = [row for row in conn.execute(stmt)]
  if len(data) == 0:
    raise HTTPException(status_code=404, detail="Item not found")
  data = dict(data[0])

  ## Getting movie genre
  query = f"SELECT GROUP_CONCAT(mg.genre) as genre FROM `movie_genres` mg WHERE movie_id={movie_id} "
  query = text(query)
  result = conn.execute(query)
  rows = [ g for g in result]
  data["genre"] = dict(rows[0])["genre"].split(",")
  conn.close()
  return {"status":"success", "data": data}


###
#  SEARCH
###

def searchForTitle(q, ASC=None):
  if(ASC == True):
    stmt = text(f'SELECT * FROM movies WHERE title LIKE "%{q}%" ORDER BY title ASC')
  elif( ASC == False ):
    stmt = text(f'SELECT * FROM movies WHERE title LIKE "%{q}%" ORDER BY title DESC')
  else:
    stmt = text(f'SELECT * FROM movies WHERE title LIKE "%{q}%"')
  print(stmt)
  conn = engine.connect()
  data = [ row for row in conn.execute(stmt)]
  return {"status":"success","length":len(data), "data":data}