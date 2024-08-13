import pytest
from dbmodels.models import User, WordleScore

def test_create_user(session):
    """Test that a User can be created and retrieved."""
    user = User(name='TestUser', user_id=12345)
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(user_id=12345).first()
    assert retrieved_user is not None
    assert retrieved_user.name == 'TestUser'
    assert retrieved_user.user_id == 12345

def test_add_wordle_score(session):
    """Test that a WordleScore can be added and correctly updates statistics."""
    user = User(name='TestUser', user_id=12345)
    session.add(user)
    session.commit()

    wordle_score = WordleScore(user_id=user.id, score=10, games_won=1, games_lost=0, total_games=1, total_guess_count=4)
    session.add(wordle_score)
    session.commit()

    retrieved_score = session.query(WordleScore).filter_by(user_id=user.id).first()
    assert retrieved_score is not None
    assert retrieved_score.score == 10
    assert retrieved_score.games_won == 1
    assert retrieved_score.total_guess_count == 4

def test_update_wordle_score(session):
    """Test updating a WordleScore."""
    user = User(name='TestUser', user_id=12345)
    session.add(user)
    session.commit()

    wordle_score = WordleScore(user_id=user.id, score=10, games_won=1, games_lost=0, total_games=1, total_guess_count=4)
    session.add(wordle_score)
    session.commit()

    # Update the score
    wordle_score.update_wordle_score(15, True, 6)
    session.commit()

    retrieved_score = session.query(WordleScore).filter_by(user_id=user.id).first()
    assert retrieved_score.games_won == 2
    assert retrieved_score.total_guess_count == 10
    assert retrieved_score.score == 25