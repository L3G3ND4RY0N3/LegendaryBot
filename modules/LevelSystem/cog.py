import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

class LevelSystem(commands.Cog, name="Level System"):
    def __innit__(self, bot):
        self.bot = bot

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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        async with aiosqlite.connect("level.db") as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.author.id,)
            )
            await db.execute(
                "UPDATE users SET msg_count = mes_count + 1 WHERE user_id = ?", (message.author.id,)
            )
            await db.execute(
                "UPDATE users SET xp = xp + ? WHERE user_id = ?", (10, message.author.id)
            )
            await db.commit()

    @app_commands.command(name="rank", description="Check your current rank!")
    async def rank(self, interaction: discord.Interaction):
        async with aiosqlite.connect("level.db") as db:
            async with db.execute("SELECT msg_count, xp FROM users WHERE user_id = ?", (interaction.user.id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Du bist noch nicht in der Datenbank", ephemeral=True)
                    return
                msg_count, xp = result

        await interaction.response.send_message(f"Du hast **{msg_count}** Nachrichten gesendet und dabei **{xp}** Erfahrung gesammelt!")



async def setup(bot):
    await bot.add_cog(LevelSystem(bot))