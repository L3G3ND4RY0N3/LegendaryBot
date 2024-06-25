from utils.filepaths import WORDLE_WORDS, WORDLE_ANSWER_WORDS
import random
from enum import Enum

#region IMPORT WORDS
def get_words(fp: str) -> set[str]:
    words = set()
    with open(fp, "r") as f:
        for line in f:
            cleaned = line.strip()
            words.add(cleaned)
    return words
#endregion

#region ENUMS
class LetterState(Enum):
    GREEN = 0
    YELLOW = 1
    GRAY = -1


class GameState(Enum):
    ONGOING = "Ongoing"
    WON = "Won"
    LOST = "Lost"


class Difficulty(Enum):
    EASY = 8
    NORMAL = 5
    HARD = 3
    GOODLUCK = 1


class WordValidity(Enum):
    TOOLONG = "Too long"
    TOOSHORT = "Too short"
    VALID = "Valid"
    INVALID = "Invalid"
#endregion

WORDS = get_words(WORDLE_WORDS)
ANSWERS = get_words(WORDLE_ANSWER_WORDS)
WORDSLIST = list(ANSWERS)
WORDLENGTH = 5


#region WORDLE CLASS
class Wordle():
    def __init__(self, max_guesses: Difficulty = Difficulty.NORMAL):
        self._secret: str = random.choice(WORDSLIST) # private
        self._guess_count = 0 # private
        self.gamestate = GameState.ONGOING # public
        self.max_guesses: int = max_guesses.value
        

    # public
    # returns a list with the letter states (colors)
    def handle_guess(self, guess: str) -> list[LetterState]:
        # if not self._word_is_valid(guess):
        #     return None
        self._guess_count += 1
        letter_state_list = self._check_guess(guess)
        if self._guess_count >= self.max_guesses and self.gamestate != GameState.WON: # if max guesses reached and game not won, lose!
            self.gamestate = GameState.LOST
        return letter_state_list
    

    # public
    # checks if the guess is a valid five-letter word
    def guess_is_valid(self, guess: str) -> WordValidity:
        if len(guess) > WORDLENGTH:
            return WordValidity.TOOLONG
        elif len(guess) < WORDLENGTH:
            return WordValidity.TOOSHORT
        elif guess.lower() not in WORDS:
            return WordValidity.INVALID
        else:
            return WordValidity.VALID

    # private
    # checks the guess letter by letter and returns a list with each letters coloring
    def _check_guess(self, guess: str) -> list[LetterState]:
        if self._is_secret(guess):
            return [LetterState.GREEN] * 5
        glist = list(guess.lower()) # guess
        slist = list(self._secret.lower()) # secret
        result = [LetterState.GRAY] * len(glist)
        unmatched_secret = []
        unmatched_guess = []

        # First pass: identify all exact matches (GREEN)
        for idx, (g_char, s_char) in enumerate(zip(glist, slist)):
            if g_char == s_char:
                result[idx] = LetterState.GREEN
            else:
                unmatched_secret.append(s_char)
                unmatched_guess.append((idx, g_char))

        # Second pass: identify partial matches (YELLOW)
        for idx, g_char in unmatched_guess:
            if g_char in unmatched_secret:
                result[idx] = LetterState.YELLOW
                unmatched_secret.remove(g_char)  # Remove to prevent duplicate matching

        return result


    # private
    # checks if the guessed word is exactly the secret word
    def _is_secret(self, guess: str) -> bool:
        if guess.lower() == self._secret.lower():
            self.gamestate = GameState.WON
            return True
        
        return False