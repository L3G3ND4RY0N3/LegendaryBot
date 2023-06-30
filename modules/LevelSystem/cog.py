import discord
from discord.ext import commands
from discord import app_commands
import random
import math
import aiosqlite
import datetime

class LevelSystem(commands.Cog, name="Level System"):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "level.db"
        self.starttime = {}

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("LevelSystem.py is ready!")    
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                msg_count INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                vc_minutes INTEGER DEFAULT 0
                )
                """
            )

            #await db.execute(
            #    """
            #    ALTER TABLE users ADD vc_minutes INTEGER DEFAULT 0
            #    """
            #) To ALTER Table to add new column!######################################

    @staticmethod
    def get_level(xp):
        lvl = 1

        while True:
            if xp >= math.ceil((6 * (lvl ** 4))/2.5):
                lvl += 1
            else:
                return lvl
            
    ########################## Message Tracker #######################################################

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        xp = random.randint(5,15)
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.author.id,)
            )
            await db.execute(
                "UPDATE users SET msg_count = msg_count + 1, xp = xp + ? WHERE user_id = ?", (xp, message.author.id)
            )
            await db.commit()

    ########################## Voice Tracker #######################################################

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            # User joined a voice channel
            start = datetime.datetime.now()
            self.starttime[member.id] = start
            print(f"{member.name} joined voice channel {after.channel.name}")
        elif before.channel is not None and after.channel is None:
            # User left a voice channel
            print(f"{member.name} left voice channel {before.channel.name}")
            # Calculate voice activity duration
            end = datetime.datetime.now()
            duration = end - self.starttime.pop(member.id, end)
            minutes = int(duration.total_seconds() / 60)
            # Award currency for unmuted time
            currency = minutes*20  # Customize how much currency to award per minute
            # Update currency in the database
            async with aiosqlite.connect(self.DB) as conn:
                async with conn.execute("UPDATE users SET vc_minutes = vc_minutes + ?, xp = xp + ? WHERE user_id = ?", (minutes, currency, member.id)):
                    await conn.commit()
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            # User switched voice channels
            print(f"{member.name} switched from voice channel {before.channel.name} to {after.channel.name}")

    ########################## Rank Command #######################################################

    @app_commands.command(name="rank", description="Check your current rank!")
    async def rank(self, interaction: discord.Interaction):
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (interaction.user.id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("You are not yet registered!", ephemeral=True)
                    return
        xp = result[0]
        lvl = self.get_level(xp)

        await interaction.response.send_message(f"You have **{xp}** XP and reached level {lvl}!")

    ########################## Leaderboard Command #######################################################

    @app_commands.command(name="leaderboard", description="Look at the leaderborad!")
    async def leaderboard(self, interaction: discord.Interaction):
        desc=""
        counter = 1
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(
                "SELECT user_id, xp, msg_count, vc_minutes FROM users WHERE msg_count > 0 ORDER BY xp DESC LIMIT 10"
            ) as cursor:
                async for user_id, xp, msg_count, vc_minutes in cursor:
                    lvl = self.get_level(xp)
                    desc += f"**{counter}.** <@{user_id}> - **{xp}** XP - **{msg_count}** message{'s' if msg_count!=1 else ''} - **{vc_minutes} ** minute{'s' if vc_minutes!=1 else ''} in voice - Level **{lvl}**\n"
                    counter += 1
        
        confedembed = discord.Embed(title="Leaderboard", description=desc, color=discord.Color.blurple())

        confedembed.set_thumbnail(url=interaction.user.avatar.url)
        confedembed.set_footer(text=f"Requested by {interaction.user.name}")

        await interaction.response.send_message(embed=confedembed)



async def setup(bot):
    await bot.add_cog(LevelSystem(bot))