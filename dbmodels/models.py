from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


DATABASE_URL = "tables/testbase.db"

engine = create_engine(DATABASE_URL, echo=True)

Base: DeclarativeBase = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    user_id = Column(Integer, unique=True)

    activities = relationship('Activity', back_populates='user')
    activities = relationship('WordleScore', back_populates='user')

    def __repr__(self) -> str:
        return f"User:{self.name}, ID: {self.user_id}"


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id')) #user.id foreign key
    minutes_in_voice = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    xp = Column(Integer, default=0)

    user = relationship("User", back_populates="activities")

    def __repr__(self) -> str:
        return f"User:{self.user}, minutes: {self.minutes_in_voice}, messages: {self.message_count}, XP: {self.xp}"
    

class WordleScore(Base):
    __tablename__ = 'wordle_scores'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id')) #user.id foreign key
    score = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)
    average_guesses = Column(Float, default=0)

    user = relationship("User", back_populates="wordle_scores")

    def __repr__(self) -> str:
        return f"User:{self.user}, Won: {self.games_won}, Lost: {self.games_lost}, Score: {self.score}, Average Guess Count: {self.average_guesses}"


# create all tables in the database
Base.metadata.create_all(engine)