from typing import Union, Set, List
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import insert, select, update, delete, text

from db import Base, engine
from models import Movies, Genre, movie_genres

Base.metadata.create_all(bind=engine)

app = FastAPI()

###  Schemas

class MoviesSchema(BaseModel):
  id : int
  title:str 
  rating:float
  class Config:
    orm_mode= True

class MovieSchema(BaseModel):
  title:str
  release_date:str
  price: Union[float, None] = None
  rating: Union[float, None ] = None
  genre: Set[int] = set()
  class Config:
    orm_mode= True


#### Routes

@app.get("/")
def getAll(sort:Union[bool,None]=None, by: Union[str,None]=None ):
  
  if(sort != None ):
    if( by != None ):
      column = text(f"movies.{by}")
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(column)
    else:
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(Movies.title)
    print(stmt)
  else:
    stmt = select(Movies.id, Movies.title, Movies.rating  )
  data = []
  conn = engine.connect()
  for row in conn.execute(stmt):
    data.append(row)

  conn.close()
  return {"status": "success", "length":len(data), "data":data}

@app.post("/")
async def addMovie(movie:MovieSchema):
  # if Validate(movie):
  #   return { "status": "failed", "msg": "Incomplete Information!"}

  stmt1 = insert(Movies).values(
    title=movie.title, release_date=movie.release_date,
    price=movie.price, rating = movie.rating  )
  stmt2 = select(Movies).where(Movies.title==movie.title, Movies.release_date==movie.release_date) 
  with engine.connect() as conn:
    conn.execute(stmt1)
    result = conn.execute(stmt2)
    row = [ row for row in result ]
    id = row[ len(row)-1 ][0]
    for genre_id in movie.genre:
      conn.execute( insert(movie_genres).values( movie_id=id, genre_id=genre_id ) )
    conn.commit()
  return { "status": "success", "data":movie}
  # return movie


@app.get("/details/{movie_id}")
def getMovieDetails(movie_id: int):
  stmt = select(Movies).where(Movies.id == movie_id)
  conn = engine.connect()
  data = [row for row in conn.execute(stmt)]
  if len(data) == 0:
    return {"status":"failed", "msg":"Invalid id"}

  query = f"SELECT GROUP_CONCAT(g.genre ORDER by g.id) as genres from genres g inner join movie_genres mg on mg.genre_id = g.id inner join movies m on m.id = mg.movie_id WHERE m.id = {movie_id} GROUP BY mg.movie_id"
  query = text(query)
  result = conn.execute(query)
  rows = [ g for g in result]
  if len(rows)>1: 
    data.append(rows[0])
  conn.close()
  return {"status":"success", "data": data}

@app.put("/update/{movie_id}")
async def addMovie(movie:MovieSchema, movie_id:int):
  stmt1 = update(Movies).where(Movies.id == movie_id ).values(
    title=movie.title, release_date=movie.release_date,
    price=movie.price, rating = movie.rating  )
  with engine.connect() as conn:
    conn.execute(stmt1)
    conn.commit()
  return { "status": "success", "data": movie.dict()}

@app.delete("/delete/{movie_id}")
def deleteMovie(movie_id:int):
  stmt = delete(Movies).where(Movies.id == movie_id)
  stmt2 = text(f"DELETE FROM `movie_genres` WHERE movie_id = {movie_id}")
  try:
    with engine.connect() as conn:
      conn.execute(stmt2)
      conn.execute(stmt)
      conn.commit()
  except:
    print("An error occured")
    return {"status":"failed", "msg":"Error"}

  return {"status":"success", "msg":"Deleted Successfully!"}


###  Search 
@app.get("/search")
def searchMovie(q: Union[str, None] = None):
  stmt = text(f'SELECT * FROM movies WHERE title LIKE "%{q}%"')
  print(stmt)
  conn = engine.connect()
  data = [ row for row in conn.execute(stmt)]
  return {"status":"success","length":len(data), "data":data}


### Validation function
# def Validate( movie ):
#   print(movie)
#   return True

