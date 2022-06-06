from fastapi import HTTPException
from sqlalchemy import insert , select, text, desc

from db import engine
from models import Movies, movie_genres


def createMovie(movie):
  if Validate(movie) == False :
    raise HTTPException(status_code=400, detail="Incomplete Information!")
  stmt1 = insert(Movies).values(
    title=movie.title, release_date=movie.release_date,
    price=movie.price, rating = movie.rating  )
  stmt2 = select(Movies).where(Movies.title==movie.title, Movies.release_date==movie.release_date) 
  
  with engine.connect() as conn:
    conn.execute(stmt1)
    result = conn.execute(stmt2)
    row = [ row for row in result ]
    id = row[ len(row)-1 ][0]
    for genre in movie.genre:
      conn.execute( insert(movie_genres).values( movie_id=id, genre=genre ) )
    conn.commit()
  return { "status": "success", "data":movie}


### UPDATE REQUEST
def updateMovieDetails(movie, movie_id):
  stmt1 = update(Movies).where(Movies.id == movie_id ).values(
    title=movie.title, release_date=movie.release_date,
    price=movie.price, rating = movie.rating)
  # Updating genre by deleting previous gnere and add updated genre
  delStmt = delete(movie_genres).where( movie_genres.c.movie_id == movie_id)
  
  with engine.connect() as conn:
    conn.execute(stmt1)
    conn.execute(delStmt)
    for genre in movie.genre:
      conn.execute( insert(movie_genres).values( movie_id=movie_id, genre=genre ) )
    conn.commit()
  return { "status": "success", "data": movie.dict()}


  ### Validation function
def Validate( movie ):
  if( len(movie.title)>60 or len(movie.title)<3 ):
    return False
  if(len(movie.genre) == 0 ):
    return False
  return True
