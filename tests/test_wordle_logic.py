import pytest
from utils.Wordle.wordle import Wordle, WordValidity, LetterState, GameState



@pytest.fixture
def invalid_guess() -> str:
    return "AAAAA"


@pytest.fixture
def secret() -> str:
    return "World"


@pytest.fixture
def normal_game(secret) -> Wordle:
    game = Wordle()
    game._secret = secret
    return game


def test_wordle_creation(normal_game: Wordle) -> None:
    assert isinstance(normal_game, Wordle)


def test_secret_property(normal_game: Wordle, secret: str):
    assert normal_game.secret == secret
    

def test_invalid_guess(normal_game: Wordle, invalid_guess: str) -> None:
    assert normal_game.guess_is_valid(invalid_guess) == WordValidity.INVALID


def test_valid_guess(normal_game: Wordle) -> None:
    assert normal_game.guess_is_valid("Earth") == WordValidity.VALID


def test_guess_too_long(normal_game: Wordle) -> None:
    assert normal_game.guess_is_valid("London") == WordValidity.TOOLONG


def test_guess_too_short(normal_game: Wordle) -> None:
    assert normal_game.guess_is_valid("Ack") == WordValidity.TOOSHORT
    

def test_capitalization(normal_game: Wordle) -> None:
    assert normal_game.guess_is_valid("eARth") == WordValidity.VALID
    assert normal_game.guess_is_valid("LonDoN") == WordValidity.TOOLONG
    assert normal_game.guess_is_valid("beRlIn") == WordValidity.TOOLONG
    assert normal_game.guess_is_valid("fluP") == WordValidity.TOOSHORT


def test_is_secret(normal_game: Wordle) -> None:
    assert normal_game._is_secret("Earth") is False
    assert normal_game._is_secret("WoRry") is False
    assert normal_game._is_secret("World") is True
    assert normal_game._is_secret("WoRlD") is True


def test_check_guess(normal_game: Wordle) -> None:
    assert normal_game._check_guess("Mumps") == [LetterState.GRAY] * 5
    assert normal_game._check_guess("World") == [LetterState.GREEN] * 5
    assert normal_game._check_guess("orwdl") == [LetterState.YELLOW] * 5
    assert normal_game._check_guess("ooooo") == [LetterState.GRAY, LetterState.GREEN, LetterState.GRAY, LetterState.GRAY, LetterState.GRAY]


def test_initial_gamestate(normal_game: Wordle) -> None:
    assert normal_game.gamestate == GameState.ONGOING


def test_defeat(normal_game: Wordle) -> None:
    normal_game._guess_count = 4
    normal_game.handle_guess("Earth")
    assert normal_game.gamestate == GameState.LOST


def test_victory(normal_game: Wordle) -> None:
    normal_game.handle_guess("World")
    normal_game.gamestate == GameState.WON