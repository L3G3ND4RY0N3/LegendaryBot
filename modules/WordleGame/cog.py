import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import settings
from utils.Wordle.wordle import WORDS, Wordle, get_valid_words

logger=settings.logging.getLogger("discord")


class WordleGame(commands.Cog, name="Wordle"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.games: dict[str, Wordle] = {} # dict with user_id, Game to keep track

    @commands.Cog.listener()
    async def on_ready(self):
        self.words = get_valid_words()
        logger.info("WordleGame.py is ready!")


async def setup(bot):
    await bot.add_cog(WordleGame(bot))