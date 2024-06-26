from constants.wordle_emojies import LETTER_EMOJIES
import discord
import utils.settings as settings
from utils.Wordle.wordle import Wordle, Difficulty, WORDLENGTH, LetterState, WordValidity, GameState
from utils.embeds.embedbuilder import warn_embed



logger=settings.logging.getLogger("discord")


def wordle_embed(user: discord.Member, game: Wordle) -> discord.Embed:
    emb = discord.Embed(color=discord.Color.blurple(), title=f"Wordle for {user.name}")
    emb.add_field(name=f"Difficulty: {game.difficulty.name.title()}", value=f"You have {game.difficulty.value} attempts to solve the wordle.")
    emb.description = "\n".join([generate_blank_lines()] * game.max_guesses)
    emb.set_footer(text=
                "To play, use command /wordle!\n"
                "To guess, write a five lettered english word in this thread\n"
                f"Author: {user.name}"
                )
    return emb

# update the embed
def update_embed(embed: discord.Embed, guess: str, letter_states: list[LetterState], game: Wordle) -> discord.Embed:
    empty_slot = generate_blank_lines()
    colored_words = generate_colored_guess(guess, letter_states)
    embed.description = embed.description.replace(empty_slot, colored_words, 1)
    num_empty_slots = embed.description.count(empty_slot)
    
    if game.gamestate == GameState.WON:
        if num_empty_slots == 0:
            embed.description += "\n\n**Phew!**"
        if num_empty_slots == 1:
            embed.description += "\n\n**Great!**"
        if num_empty_slots == 2:
            embed.description += "\n\n**Splendid!**"
        if num_empty_slots == 3:
            embed.description += "\n\n**Impressive!**"
        if num_empty_slots == 4:
            embed.description += "\n\n**Magnificent!**"
        if num_empty_slots >= 5:
            embed.description += "\n\n**Genius!**"
    elif game.gamestate == GameState.LOST:
        embed.description += f"\n\n**Better luck next time!** \n**The secret word was {game.secret}**"

    return embed

#region UTILITIES

# generates blank lines for the initial embed
def generate_blank_lines() -> str:
    return "◻️" * WORDLENGTH


def generate_colored_guess(guess: str, letter_state_list: list[LetterState]) -> str:
    colored = []
    for idx, char in enumerate(guess):
        colored.append(LETTER_EMOJIES[letter_state_list[idx]][char])
    return "".join(colored)


def validity_of_guess_embed(guess: str, game: Wordle) -> discord.Embed:
        validity: WordValidity = game.guess_is_valid(guess)
        match validity:
            case WordValidity.TOOLONG:
                emb = warn_embed(f"Your guess was too long!")
            case WordValidity.TOOSHORT:
                emb = warn_embed(f"Your guess was too short!")
            case WordValidity.INVALID:
                emb = warn_embed(f"Your guess was not a valid word!")
            case WordValidity.VALID:
                emb = None
        return emb

#endregion