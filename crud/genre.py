from db import engine
from typing import Union, Set
from sqlalchemy import insert , select, update, delete, text, desc

def getByGenre(genre):
  conn = engine.connect()
  result = conn.execute(text(
    'SELECT m.title,MAX(m.rating) ,MAX(m.release_date), GROUP_CONCAT(mg.genre) as genre FROM movies m INNER JOIN movie_genres mg ON mg.movie_id = m.id WHERE mg.genre in ("Action","Drama") GROUP BY m.title'
  ))
  result = [r for r in result]
  print(result)
  conn.close()
  return "working" 