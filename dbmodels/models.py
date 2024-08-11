import discord
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, get_db_session


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    user_id = Column(Integer, unique=True)

    members = relationship('Member', back_populates='user')
    wordle_scores = relationship('WordleScore', back_populates='user')

    def __repr__(self) -> str:
        return f"User:{self.name}, ID: {self.user_id}"
    

    @classmethod
    def create_user(cls, dcuser: discord.User) -> "User":
        """Creates a new instance of the User db Class and saves it to the database
        """
        with next(get_db_session()) as session:
            user = User(name=dcuser.global_name, user_id=dcuser.id)
            session.add(user)
            session.commit()
            return user
    
    @classmethod
    def get_or_create_user(cls, dcuser: discord.User) -> "User":
        """Tries to retrieve a User from the database by filtering by the users discord id.
        If None is found, a new one is created and stored in the database

        Args:
            dcuser (discord.User): The discord User class, as Member inherits from it, discord.Member can also be passed

        Returns:
            User: Either an existing User or a newly created one
        """
        with next(get_db_session()) as session:
            user: User = session.query(cls).filter_by(user_id=dcuser.id).first()
            if not user:
                user = cls.create_user(dcuser)
                session.add(user)
                session.commit()
            return user


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
    

class WordleScore(Base):
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
    def add_score(self, score_increment: int) -> None:
        """Adds to the user's score, ensuring the increment is positive."""
        if score_increment < 0:
            raise ValueError("Score increment cannot be negative")
        if not self.score:
            self.score = 0
        self.score += score_increment


    def add_game(self, game_won: bool) -> None:
        """Records the outcome of a game, updating the total games and win/loss count."""
        self.games_won = (self.games_won or 0) + (1 if game_won else 0)
        self.games_lost = (self.games_lost or 0) + (1 if not game_won else 0)
        self.total_games = (self.total_games or 0) + 1


    def add_total_guesses(self, guess_count: int) -> None:
        """Adds to the total guess count."""
        if not self.total_guess_count:
            self.total_guess_count = 0
        self.total_guess_count += guess_count

    
    def calculate_average_guess_count(self, guess_count: int) -> None:
        """Calculates the average number of guesses per game."""
        if self.total_games > 0:
            self.average_guesses += (guess_count - self.average_guesses) / self.total_games


    def update_wordle_score(self, score_increment:int, game_won: bool, guess_count: int) -> None:
        """Updates the user's score and game statistics."""
        self.add_score(score_increment)
        self.add_game(game_won)
        self.add_total_guesses(guess_count)
        self.calculate_average_guess_count(guess_count)
#endregion
    
#region CLASS METHODS    
    @classmethod
    def create_wordle_score(cls, user: User, score_increment: int = 0, game_won: bool = None, guess_count: int = 0) -> "WordleScore":
        """Creates a new instance of WordleScore and records it to the database

        Args:
            dcuser (User): A dbmodels.model.User instance
            score_increment (int, optional): The score increment from winning the game. Defaults to 0.
            game_won (bool, optional): Whether the game was won/lost. Defaults to None, if executed via another command and not a game.
            guess_count (int, optional): The number of guesses for the game. Defaults to 0.

        Returns:
            WordleScore: A WordleScore object.
        """
        with next(get_db_session()) as session:
            wordle_score = WordleScore(
                user_id=user.id,
                score=score_increment,
                total_guess_count=guess_count, 
                average_guesses=guess_count
                )
            session.add(wordle_score)
            # if the creation stems from a game and not another command, record the game
            if game_won is not None:
                wordle_score.add_game(game_won)
            session.commit()
            return wordle_score

    @classmethod
    def update_or_create_wordle_score(cls, dcuser: discord.User, score_increment: int, game_won: bool, guess_count: int = 0) -> None:
        """Responsible for updating the user wordle_score

        Args:
            dcuser (discord.User): A discord User|Member as Member inherits from user
            score (int): The score that will be added to the database
        """
        with next(get_db_session()) as session:
            # merge the sessions or get a DetachedInstanceError later!
            user = User.get_or_create_user(dcuser)

            wordle_score = session.query(cls).filter_by(user_id=user.id).first()

            if wordle_score:
                wordle_score.update_wordle_score(score_increment, game_won, guess_count)
            else:
                wordle_score = WordleScore.create_wordle_score(user, score_increment, game_won, guess_count)

            session.commit()

    @classmethod
    def get_or_create_wordle_score_for_user(cls, dcuser: discord.User) -> "WordleScore":
        """Retrieves a wordle score instance for a dc User or creates a new Instance with no games played"""
        with next(get_db_session()) as session:
            user = User.get_or_create_user(dcuser)
            wordle_score = session.query(cls).filter_by(user_id=user.id).first()
            if not wordle_score:
                wordle_score = WordleScore.create_wordle_score(dcuser)

            return wordle_score
#endregion