import discord
from dbmodels.base import SessionLocal
from dbmodels.models import User, WordleScore
from .dbservice import DatabaseService


db_service = DatabaseService(SessionLocal)

def handle_wordle_score(dcuser: discord.User, score_increment: int = 0, game_won: bool = None, guess_count: int = None, update: bool = False) -> dict | None:
    """Handles the creation, getting and updating of a Wordle Score for a user

    Args:
        dcuser (discord.User): A discord User | Member
        score_increment (int, optional): The score of the wordle game. Defaults to 0.
        game_won (bool, optional): Whether the game was won or not. Defaults to None.
        guess_count (int, optional): The guesses for the game. Defaults to None.
        update (bool, optional): Whether a game should be recorded or not. Defaults to False. If False, Return Value is NONE!

    Returns:
        dict | None: If a game was recorded, nothing gets returned, as the score is simply updated. Else return a dictionary with the data for the users WordleScore
    """
    with db_service.session_scope() as session:
        user = db_service.get_or_create(User, user_id=dcuser.id, name=dcuser.global_name)
        session.add(user)
        wordle_score = db_service.get_or_create(WordleScore, user_id=user.id)
        session.add(wordle_score)
        
        if wordle_score and update:
            wordle_score.update_wordle_score(score_increment, game_won, guess_count)

        if not update:
            return wordle_score.to_dict()