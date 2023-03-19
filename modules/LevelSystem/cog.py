import discord
from discord.ext import commands
from discord import app_commands
import random
import math
import aiosqlite

class LevelSystem(commands.Cog, name="Level System"):
    def __innit__(self, bot):
        self.bot = bot
        self.DB = "level.db"

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("LevelSystem.py is ready!")    
        async with aiosqlite.connect("level.db") as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                msg_count INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
                )
                """
            )

    @staticmethod
    def get_level(xp):
        lvl = 1

        while True:
            if xp >= math.ceil((6 * (lvl ** 4))/2.5):
                lvl += 1
            else:
                return lvl

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        xp = random.randint(5,15)
        async with aiosqlite.connect("level.db") as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.author.id,)
            )
            await db.execute(
                "UPDATE users SET msg_count = msg_count + 1, xp = xp + ? WHERE user_id = ?", (xp, message.author.id)
            )
            await db.commit()

    @app_commands.command(name="rank", description="Check your current rank!")
    async def rank(self, interaction: discord.Interaction):
        async with aiosqlite.connect("level.db") as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (interaction.user.id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Du bist noch nicht in der Datenbank", ephemeral=True)
                    return
        xp = result[0]
        lvl = self.get_level(xp)

        await interaction.response.send_message(f"Du hast **{xp}** Erfahrung gesammelt udn bist Level {lvl}!")

    @app_commands.command(name="leaderboard", description="Look at the leaderborad!")
    async def leaderboard(self, interaction: discord.Interaction):
        desc=""
        counter = 1
        async with aiosqlite.connect("level.db") as db:
            async with db.execute(
                "SELECT user_id, xp, msg_count FROM users WHERE msg_count > 0 ORDER BY xp DESC LIMIT 10"
            ) as cursor:
                async for user_id, xp, msg_count in cursor:
                    lvl = self.get_level(xp)
                    desc += f"**{counter}.** <@{user_id}> - **{xp}** XP - **{msg_count}** Message(s) - Level **{lvl}**\n"
                    counter += 1
        
        confedembed = discord.Embed(title="Leaderboard", description=desc, color=discord.Color.blurple())

        confedembed.set_thumbnail(url=interaction.user.avatar.url)
        confedembed.set_footer(text=f"Requested by {interaction.user.name}")

        await interaction.response.send_message(embed=confedembed)



async def setup(bot):
    await bot.add_cog(LevelSystem(bot))