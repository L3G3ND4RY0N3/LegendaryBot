from asyncio import sleep
from dataclasses import dataclass
import discord
from discord.ext import commands
from discord import app_commands
from utils import settings
from utils.Wordle.wordle import Wordle, Difficulty, GameState
from utils.embeds.embedbuilder import warn_embed, forbidden_embed, success_embed
from utils.embeds.wordle_embed import wordle_embed, validity_of_guess_embed, update_embed
from utils.views.wordle_view import WordleView

logger=settings.logging.getLogger("discord")


class WordleGame(commands.Cog, name="Wordle"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.games: dict[int, PlayerData] = {} # dict with user_id, Games and threads to keep track of ongoing games and their threads

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")


#region EVENTS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        user = message.author
        # if user is not playing a wordle game or is a bot, quit
        if user.id not in self.games or message.author.bot:
            return
        thread = self.games[user.id].thread
        # if message is not send in the users game thread, quit
        if message.channel.id != thread.id:
            return
        # get users game
        game = self.games[user.id].game
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
        game_embed = self.games[user.id].embed

        # edit game embed
        game_embed = update_embed(game_embed, guess, letter_states, game)
        game_message = self.games[user.id].message
        await game_message.edit(embed=game_embed)

        # update game and embed in dictionary and delete thread if game is over
        if not self.update_games_dictionary(user.id, game, thread, game_embed, game_message):
            await self.del_game_thread(thread, f"Wordle {game.gamestate.value.lower()}", 10)
        return
    

    # called when the thread is deleted by any means to remove the associated game, if any
    @commands.Cog.listener()
    async def on_thread_remove(self, thread: discord.Thread) -> None:
        if id := self.find_player_id_by(thread=thread):
            self.games.pop(id)
        return


    # called when the game message is deleted to delete the game too!
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if id := self.find_player_id_by(message=message):
            thread = self.games[id].thread
            self.games.pop(id)
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
        if ctx.user.id in self.games:
            thread = self.games[ctx.user.id].thread
            if thread and thread in thread.guild.threads: # thread was not deleted -> game is ongoing
                emb = warn_embed(f"You already have an ongoing game in {thread.mention}!")
                await ctx.response.send_message(embed=emb, ephemeral=True, view=WordleView(ctx, self.bot, self.games[ctx.user.id]))
                print(self.games[ctx.user.id].game)
                return
        
        # create public thread, where only the interacting user can write
        thread = await self.create_wordle_thread(ctx)

        if not thread:
            return
        
        game = Wordle(Difficulty[difficulty.value])
        emb = wordle_embed(ctx.user, game)

        try:
            message = await thread.send(embed=emb)
        except discord.Forbidden as e:
            logger.error(f"Unable to send messages in thread {thread.name} in guild {thread.guild.name}")
            logger.exception(f"{e}")
            fail_emb = warn_embed(f"Unable to send message in {thread.name}")
            await ctx.response.send_message(embed=fail_emb, ephemeral=True)
            return
        
        if self.update_games_dictionary(ctx.user.id, game, thread, emb, message):
            suc_emb = success_embed(f"Created wordle in {thread.mention}")
            await ctx.response.send_message(embed=suc_emb)
            return
        else:
            error_emb = warn_embed("Something went wrong, please try again later")
            await ctx.response.send_message(embed=error_emb, ephemeral=True)
            return
#endregion


#region METHODS

    def update_games_dictionary(self, user_id: int, game: Wordle, thread: discord.Thread, embed: discord.Embed, message: discord.Message) -> bool:
        # if new game, set all variables
        if user_id not in self.games or game.gamestate == GameState.ONGOING:
            self.games[user_id] = PlayerData(game=game, thread=thread, embed=embed, message=message)
            return True
        
        # if game was aborted via button, restart if /wordle is used
        if user_id in self.games and thread != self.games[user_id].thread:
            self.games[user_id] = PlayerData(game=game, thread=thread, embed=embed, message=message)
            return True
        
        # if game is over remove the user and their game from the dict
        if game.gamestate != GameState.ONGOING:
            self.games.pop(user_id)
            return False
        
        # if thread, message or embed is gone, abort
        if not thread or not embed or not message:
            self.games.pop(user_id)
            return False
        

    def find_player_id_by(self, thread: discord.Thread = None, embed: discord.Embed = None, message: discord.Message = None) -> int | None:
        # if no input, return None
        if not thread and not embed and not message:
            return None
        
        for player_id, player_data in self.games.items():
            if player_data.thread == thread:
                return player_id
            
            if player_data.embed == embed:
                return player_id
            
            if player_data.message == message:
                return player_id
            
        # if nothing found return None    
        return None

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


@dataclass
class PlayerData():
    game: Wordle = None
    thread: discord.Thread = None
    embed: discord.Embed = None
    message: discord.Message = None