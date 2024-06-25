from asyncio import sleep
import discord
from discord.ext import commands
from discord import app_commands
from dataclasses import dataclass, field
from enum import Enum
from utils import settings
from utils.Wordle.wordle import Wordle, get_words, Difficulty, GameState
from utils.embeds.embedbuilder import warn_embed, forbidden_embed, success_embed
from utils.embeds.wordle_embed import wordle_embed, validity_of_guess_embed, update_embed
from typing import Dict, Union

logger=settings.logging.getLogger("discord")


class WordleGame(commands.Cog, name="Wordle"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.games: dict[int, GameAndThreadDict] = {} # dict with user_id, Games and threads to keep track of ongoing games and their threads

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("WordleGame.py is ready!")


#region EVENTS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        user = message.author
        # if user is not playing a wordle game or is a bot, quit
        if user.id not in self.games or message.author.bot:
            return
        thread = self.games[user.id].games_and_threads[GAMEKEYS.THREAD]
        # if message is not send in the users game thread, quit
        if message.channel.id != thread.id:
            return
        # get users game
        game = self.games[user.id].games_and_threads[GAMEKEYS.GAME]
        #get guess from message
        guess = message.content.lower()
        # check if guess is a valid 5 letter english word
        emb = validity_of_guess_embed(guess, game)

        if emb:
            await message.reply(embed=emb, delete_after=5)
            return
        
        
        # check the guess and update the gamestate, if game is won, lost or continuing
        letter_states = game.handle_guess(guess)

        # retrieve the game embed for edit
        game_embed = self.games[user.id].games_and_threads[GAMEKEYS.EMBED]
        print(game._secret)
        # edit game embed
        game_embed = update_embed(game_embed, guess, letter_states, game)
        game_message = self.games[user.id].games_and_threads[GAMEKEYS.MESSAGE]
        await game_message.edit(embed=game_embed)

        # update game and embed in dictionary and delete thread if game is over
        if not self.update_game_dictionary(user.id, game, thread, game_embed, game_message):
            try:
                # wait 10 seconds to delete thread
                await sleep(10)
                await thread.delete(reason=f"Wordle {game.gamestate.value.lower()}")
            except discord.Forbidden as e:
                logger.error(f"Unable to delete thread {thread.name} in guild {message.guild.name}")
                logger.exception(f"{e}")
        return
    

    @commands.Cog.listener()
    async def on_thread_remove(self, thread: discord.Thread) -> None:
        #TODO: remove game from dict, when thread gets deleted by other means
        return

#endregion


#region COMMANDS

    @app_commands.command(name="wordle", description="starts a game of wordle")
    @app_commands.describe(difficulty="Select a difficulty for the game, which determines the number of tries you have.")
    @app_commands.choices(difficulty=[
    app_commands.Choice(name="Easy", value="EASY"),
    app_commands.Choice(name="Normal", value="NORMAL"),
    app_commands.Choice(name="Hard", value="HARD"),
    app_commands.Choice(name="Good Luck", value="GOODLUCK"),
    ])
    async def wordle(self, ctx:discord.Interaction, difficulty: app_commands.Choice[str]) -> None:
        if ctx.user.id in self.games:
            thread = self.games[ctx.user.id].games_and_threads[GAMEKEYS.THREAD]
            emb = warn_embed(f"You already have an ongoing game in {thread.mention}!")
            await ctx.response.send_message(embed=emb, ephemeral=True)
            return
        
        # create public thread, where only the interacting user can write
        thread = await self.create_wordle_thread(ctx)

        if not thread:
            return
        
        game = Wordle(Difficulty[difficulty.value])
        selected_difficulty = Difficulty[difficulty.value]
        emb = wordle_embed(ctx.user, game, selected_difficulty)

        try:
            message = await thread.send(embed=emb)
        except discord.Forbidden as e:
            logger.error(f"Unable to send messages in thread {thread.name} in guild {thread.guild.name}")
            logger.exception(f"{e}")
            fail_emb = warn_embed(f"Unable to send message in {thread.name}")
            await ctx.response.send_message(embed=fail_emb, ephemeral=True)
            return
        
        if self.update_game_dictionary(ctx.user.id, game, thread, emb, message):
            suc_emb = success_embed(f"Created wordle in {thread.mention}")
            await ctx.response.send_message(embed=suc_emb)
            return
        else:
            error_emb = warn_embed("Something went wrong, please try again later")
            await ctx.response.send_message(embed=error_emb, ephemeral=True)
            return
#endregion


#region METHODS
    def update_game_dictionary(self, user_id: int, game: Wordle, thread: discord.Thread, embed: discord.Embed, message: discord.Message) -> bool:
        if user_id not in self.games or game.gamestate == GameState.ONGOING:
            self.games[user_id] = GameAndThreadDict(games_and_threads={GAMEKEYS.GAME: game, GAMEKEYS.THREAD: thread, GAMEKEYS.EMBED: embed, GAMEKEYS.MESSAGE: message})
            return True
        # if game is over remove the user and their game from the dict
        if game.gamestate != GameState.ONGOING:
            self.games.pop(user_id)
            return False
        
        # if thread, message or embed is gone, abort
        if not thread or not embed or not message:
            self.games.pop(user_id)
            return False
#endregion

#region STATIC METHODS
    @staticmethod
    async def create_wordle_thread(ctx: discord.Interaction) -> discord.Thread | None:
        try:
            thread: discord.Thread = await ctx.channel.create_thread(
                name=f"Wordle for {ctx.user.name}",
                type=discord.ChannelType.public_thread
            )
            return thread
        except discord.Forbidden as e:
            logger.error(f"Unable to create public thread in guild {ctx.guild} in channel {ctx.channel}")
            logger.exception(f"{e.text}")
            # TODO: Add logging to error guild logging
            emb = forbidden_embed(f"Unable to create public thread in guild {ctx.guild} in channel {ctx.channel}")
            await ctx.response.send_message(embed=emb, ephemeral=True)
            return None
        
#endregion


async def setup(bot):
    await bot.add_cog(WordleGame(bot))


class GAMEKEYS(Enum):
    GAME = "Game"
    THREAD = "Thread"
    EMBED = "Embed"
    MESSAGE = "Message"


@dataclass
class GameAndThreadDict():
    games_and_threads: Dict[GAMEKEYS, Union[Wordle, discord.Thread, discord.Embed, discord.Message]] = field(default_factory=dict)

    # def __contains__(self, entry: Union[Wordle, discord.Thread, discord.Embed, discord.Message]):
    #     for sub_dict in self.games_and_threads.values():
    #         if entry in sub_dict:
    #             return True
    #     return False