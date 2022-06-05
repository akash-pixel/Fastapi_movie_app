from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Set, List
from sqlalchemy import insert , select, update, delete, text, desc

from db import Base, engine
from models import Movies, movie_genres

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
  "http://localhost:3000"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"],
)

# Schemas
class MovieSchema(BaseModel):
  title:str
  release_date:str
  price: Union[float, None] = None
  rating: Union[float, None ] = None
  genre: Set[str] = set()
  class Config:
    orm_mode= True

#### Routes

@app.get("/", status_code=200)
def getAll(ASC:Union[bool,None]=None, sort_by: Union[str,None]=None ):
  
  if(ASC == True ):
    if( sort_by != None ):
      column = text(f"movies.{sort_by}")
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(column)
    else:
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(Movies.title)
    print(stmt)
  # Asc = false will used for sorting in descending order  
  elif( ASC == False ):
    if( sort_by != None ):
      column = text(f"movies.{sort_by}")
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(desc(column))
    else:
      stmt = select(Movies.id, Movies.title, Movies.rating).order_by(desc(Movies.title))
    print(stmt)
  else:
    stmt = select(Movies.id, Movies.title, Movies.rating  )

  data = []
  conn = engine.connect()
  for row in conn.execute(stmt):
    data.append(row)

  conn.close()
  return {"status": "success", "length":len(data), "data":data}

# POST
@app.post("/", status_code =201)
async def addMovie(movie:MovieSchema):
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

# Movie DETAILS
@app.get("/details/{movie_id}", status_code=200)
def getMovieDetails(movie_id: int):
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

####  PUT REQUEST
@app.put("/update/{movie_id}", status_code =201)
async def updateMovie(movie:MovieSchema, movie_id:int):
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

# DELETE
@app.delete("/delete/{movie_id}", status_code=204)
def deleteMovie(movie_id:int):
  stmt = delete(Movies).where(Movies.id == movie_id)
  stmt2 = delete(movie_genres).where(movie_genres.c.id == movie_id)
  try:
    with engine.connect() as conn:
      conn.execute(stmt2)
      conn.execute(stmt)
      conn.commit()
  except:
    raise HTTPException(status_code=500, detail="Server Error")
    
  return {"status":"success", "msg":"Deleted Successfully!"}


###  Search 
@app.get("/search", status_code=200)
def searchMovie(q: Union[str, None] = None, ASC:Union[bool,None]=None ):

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

@app.get("*", status_code=400)
def notFound():
  return HTTPException(status_code=404, detail="Page Not Found")


### Validation function
def Validate( movie ):
  if( len(movie.title)>60 or len(movie.title)<3 ):
    return False
  if(len(movie.genre) == 0 ):
    return False
  return True

