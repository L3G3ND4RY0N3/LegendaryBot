import discord
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, get_db_session
from utils.dbhelpers.mixin import SerializerMixin

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    user_id = Column(Integer, unique=True)

    members = relationship('Member', back_populates='user')
    wordle_scores = relationship('WordleScore', back_populates='user')

    def __repr__(self) -> str:
        return f"User:{self.name}, ID: {self.user_id}"


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id')) #user.id foreign key
    minutes_in_voice = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    xp = Column(Integer, default=0)

    member = relationship("Member", back_populates="activities")

    def __repr__(self) -> str:
        return f"Member:{self.member.server_name}, minutes: {self.minutes_in_voice}, messages: {self.message_count}, XP: {self.xp}"
    

class WordleScore(Base, SerializerMixin):
    __tablename__ = 'wordle_scores'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id')) #user.id foreign key
    score = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_guess_count = Column(Integer, default=0)
    average_guesses = Column(Float, default=0)

    user = relationship("User", back_populates="wordle_scores")

    def __repr__(self) -> str:
        return f"User:{self.user}, Won: {self.games_won}, Lost: {self.games_lost}, Score: {self.score}, Average Guess Count: {self.average_guesses:.2}"
    
#region INSTANCE METHODS
    def _add_score(self, score_increment: int) -> None:
        """Adds to the user's score, ensuring the increment is positive."""
        if score_increment < 0:
            raise ValueError("Score increment cannot be negative")
        if not self.score:
            self.score = 0
        self.score += score_increment


    def _add_game(self, game_won: bool) -> None:
        """Records the outcome of a game, updating the total games and win/loss count."""
        self.games_won = (self.games_won or 0) + (1 if game_won else 0)
        self.games_lost = (self.games_lost or 0) + (1 if not game_won else 0)
        self.total_games = (self.total_games or 0) + 1


    def _add_total_guesses(self, guess_count: int) -> None:
        """Adds to the total guess count."""
        if not self.total_guess_count:
            self.total_guess_count = 0
        self.total_guess_count += guess_count

    
    def _calculate_average_guess_count(self, guess_count: int) -> None:
        """Calculates the average number of guesses per game."""
        if self.total_games > 0:
            self.average_guesses += (guess_count - self.average_guesses) / self.total_games


    def update_wordle_score(self, score_increment: int, game_won: bool, guess_count: int) -> None:
        """Updates the user's score and game statistics."""
        if score_increment is not None:
            self._add_score(score_increment)
        if game_won is not None:
            self._add_game(game_won)
        if guess_count is not None:
            self._add_total_guesses(guess_count)
            self._calculate_average_guess_count(guess_count)
#endregion