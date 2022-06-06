from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Set
from db import Base, engine

# Operations
from crud.get import getAllMovies, getMovie, searchForTitle
from crud.movie import createMovie, updateMovieDetails
from crud.deleteMovie import delete

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
  "*",
  "http://localhost:3000"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"],
)

#########        Schema      #########
class MovieSchema(BaseModel):
  title:str
  release_date:str
  price: Union[float, None] = None
  rating: Union[float, None ] = None
  genre: Set[str] = set()
  class Config:
    orm_mode= True


#########         Routes         #########

#  GET
@app.get("/", status_code=200)
async def getAll(ASC:Union[bool,None]=None, sort_by: Union[str,None]=None ):
  result = getAllMovies(ASC, sort_by)
  return result

@app.get("/details/{movie_id}", status_code=200)
async def getMovieDetails(movie_id: int):
  result = getMovie(movie_id)
  return result

@app.get("/search", status_code=200)
async def search(q: str, ASC:Union[bool,None]=None ):
  result = searchForTitle(q, ASC)
  return result

### POST
@app.post("/", status_code =201)
async def AddMovie(movie:MovieSchema):
  result = createMovie(movie)
  return result

### PUT
@app.put("/update/{movie_id}", status_code =201)
async def updateMovie(movie:MovieSchema, movie_id:int):
  result = updateMovieDetails(movie, movie_id)
  return result

### DELETE
@app.delete("/delete/{movie_id}", status_code=200)
async def deleteMovie(movie_id:int):
  result = delete(movie_id)
  return result

### PAGE NOT FOUND
@app.get("*", status_code=200)
def notFound():
  return HTTPException(status_code=404, detail="Page Not Found")


