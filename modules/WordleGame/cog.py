from asyncio import sleep
from dataclasses import dataclass
import discord
from discord.ext import commands
from discord import app_commands

from dbmodels.models import WordleScore
from utils import settings
from utils.Wordle.wordle import Wordle, Difficulty, GameState
from utils.embeds.embedbuilder import warn_embed, forbidden_embed, success_embed
from utils.embeds.wordle_embed import wordle_embed, validity_of_guess_embed, update_embed
from utils.views.wordle_view import WordleView
from utils.structs.WordleData import PlayerData, WordleData

logger=settings.logging.getLogger("discord")


class WordleGame(commands.Cog, name="Wordle"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.wordle_data: WordleData = WordleData()  # dict with user_id, Games and threads to keep track of ongoing games and their threads

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")


#region EVENTS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        user = message.author
        # if user is not playing a wordle game or is a bot, quit
        if user.id not in self.wordle_data.games or message.author.bot:
            return
        thread = self.wordle_data.games[user.id].thread
        # if message is not send in the users game thread, quit
        if message.channel.id != thread.id:
            return
        # get users game
        game = self.wordle_data.games[user.id].game
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
        game_embed = self.wordle_data.games[user.id].embed

        # edit game embed
        game_embed = update_embed(game_embed, guess, letter_states, game)
        game_message = self.wordle_data.games[user.id].message
        await game_message.edit(embed=game_embed)

        # player_data = PlayerData(game=game, thread=thread, embed=game_embed, message=game_message)

        # update game and embed in dictionary and delete thread if game is over
        if not game.gamestate == GameState.ONGOING:
            # updating the score of the user in the database
            WordleScore.update_or_create_wordle_score(user, game.score, game.game_is_won, game.guess_count)
            await self.del_game_thread(thread, f"Wordle {game.gamestate.value.lower()}", 10)
            self.wordle_data.update_games_dictionary(user.id)
        return
    

    # called when the thread is deleted by any means to remove the associated game, if any
    @commands.Cog.listener()
    async def on_thread_remove(self, thread: discord.Thread) -> None:
        if id := self.wordle_data.find_player_id_by(thread=thread):
            self.wordle_data.update_games_dictionary(id)
        return


    # called when the game message is deleted to delete the game too!
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if id := self.wordle_data.find_player_id_by(message=message):
            thread = self.wordle_data.games[id].thread
            self.wordle_data.update_games_dictionary(id)
            await self.del_game_thread(thread, "Game message was deleted", 1)            
        return

#endregion


#region COMMANDS

    @app_commands.command(name="wordle", description="starts a game of wordle")
    @app_commands.describe(difficulty="Select a difficulty for the game, which determines the number of tries you have.")
    @app_commands.choices(difficulty=[
        app_commands.Choice(
            name=diff.name.title(),
            value=diff.name) for diff in Difficulty]
        )
    async def wordle(self, ctx:discord.Interaction, difficulty: app_commands.Choice[str]) -> None:
        if ctx.user.id in self.wordle_data.games:
            thread = self.wordle_data.games[ctx.user.id].thread
            if thread and thread in thread.guild.threads: # thread was not deleted -> game is ongoing
                emb = warn_embed(f"You already have an ongoing game in {thread.mention}!")
                await ctx.response.send_message(embed=emb, ephemeral=True, view=WordleView(ctx, self.bot, self.wordle_data))
                return
            else:
                # thread deleted, pop game from data
                self.wordle_data.update_games_dictionary(ctx.user.id)
        
        # create public thread, where only the interacting user can write
        thread = await self.create_wordle_thread(ctx)

        if not thread:
            return
        
        game = Wordle(Difficulty[difficulty.value])
        wordle_emb = wordle_embed(ctx.user, game)

        try:
            message = await thread.send(embed=wordle_emb)
        except discord.Forbidden as e:
            logger.error(f"Unable to send messages in thread {thread.name} in guild {thread.guild.name}")
            logger.exception(f"{e}")
            fail_emb = warn_embed(f"Unable to send message in {thread.name}")
            await ctx.response.send_message(embed=fail_emb, ephemeral=True)
            return
        
        # instanciate player_data
        player_data = PlayerData(game=game, thread=thread, embed=wordle_emb, message=message)

        if self.wordle_data.update_games_dictionary(ctx.user.id, player_data):
            suc_emb = success_embed(f"Created wordle in {thread.mention}")
            await ctx.response.send_message(embed=suc_emb)
            return
        # if something went wrong, delete thread and game from data
        else:
            error_emb = warn_embed("Something went wrong, please try again later")
            await ctx.response.send_message(embed=error_emb, ephemeral=True)
            await thread.delete(reason="Error in wordle creation")
            self.wordle_data.update_games_dictionary(ctx.user.id)
            return
#endregion

#region STATIC METHODS
    @staticmethod
    async def create_wordle_thread(ctx: discord.Interaction) -> discord.Thread | None:
        try:
            thread: discord.Thread = await ctx.channel.create_thread(
                name=f"Wordle for {ctx.user.name}",
                type=discord.ChannelType.public_thread
            )
            await thread.add_user(ctx.user)
            return thread
        except discord.Forbidden as e:
            logger.error(f"Unable to create public thread in guild {ctx.guild} in channel {ctx.channel}")
            logger.exception(f"{e.text}")
            # TODO: Add logging to error guild logging
            emb = forbidden_embed(f"Unable to create public thread in guild {ctx.guild} in channel {ctx.channel}")
            await ctx.response.send_message(embed=emb, ephemeral=True)
            return None
        

    @staticmethod
    async def del_game_thread(thread: discord.Thread, msg: str, time: float) -> None:
        try:
            await sleep(time)
            await thread.delete(reason=msg) # msg is reason for audit log
        except discord.Forbidden as e:
            logger.error(f"Unable to delete thread {thread.name} in guild {thread.guild.name}")
            logger.exception(f"{e}")
        
#endregion


async def setup(bot):
    await bot.add_cog(WordleGame(bot))