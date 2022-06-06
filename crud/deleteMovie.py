from fastapi import HTTPException
from sqlalchemy import text

from db import engine

def delete(movie_id):
  # stmt1 to delete movie id from movie_genres
  # stmt2 for delete movie_id from movies
  stmt1 = text(f"DELETE from movie_genres where movie_genres.movie_id = {movie_id}")
  stmt2 = text(f"DELETE FROM movies where movies.id = {movie_id}")
  
  try:
    with engine.connect() as conn:
      conn.execute(stmt1)
      conn.execute(stmt2)
      conn.commit()
  except:
    raise HTTPException(status_code=500, detail="Server Error")
    
  return {"status":"success", "msg":"Deleted Successfully!"}