from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

movie_genres = Table(
  "movie_genres",
  Base.metadata,
  Column("id", Integer, primary_key=True),
  Column("movie_id", ForeignKey("movies.id")),
  Column("genre", String)
)

class Movies(Base):
  __tablename__ = "movies"
  id = Column( Integer, primary_key=True, index=True)
  title = Column( String(60), nullable=False)
  release_date = Column( Date )
  price = Column( Float )
  rating = Column( Float )
  # genre = relationship("movie_genre", secondary= movie_genres)

