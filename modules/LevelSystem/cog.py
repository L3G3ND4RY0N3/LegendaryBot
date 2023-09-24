import discord
from discord.ext import commands, tasks
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
        self.update_member_points.start()
        self.check_members_in_voice.start()


    def cog_unload(self):
        self.update_member_points.cancel()

    def cog_unload(self):
        self.check_members_in_voice.cancel()

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

    ##################################### Tasks #################################################################

    @tasks.loop(minutes=3)
    async def check_members_in_voice(self):
        guilds = self.bot.guilds
        vc_channels = []
        for guild in guilds:
            for vc_channel in guild.voice_channels:
                vc_channels.append(vc_channel)
        vc_channels_count = len(vc_channels)
        new_user_count = 0
        for channel in vc_channels:
            for member in channel.members:
                if member.id not in self.starttime.keys():
                    new_user_count+=1
                    self.starttime[member.id] = datetime.datetime.now()
        print(f"Checked {vc_channels_count} voice channels and added {new_user_count} users!") #TODO: future log entry

    @check_members_in_voice.before_loop
    async def before_check_members_in_voice_task(self):
        print("Check user loop is waiting for the bot to load...") #TODO: future log entry
        await self.bot.wait_until_ready()


    @tasks.loop(minutes=5)
    async def update_member_points(self):
        if not bool(self.starttime):
            print("No members in voice!") #TODO: futere log entry
            return
        user_count = len(self.starttime.keys())
        for key in self.starttime:
            update_time = datetime.datetime.now()
            member_id = int(key)
            duration = update_time - self.starttime[member_id]
            minutes = int(duration.total_seconds() / 60)
            # Award currency for unmuted time
            currency = minutes*20
            async with aiosqlite.connect(self.DB) as conn:
                async with conn.execute("UPDATE users SET vc_minutes = vc_minutes + ?, xp = xp + ? WHERE user_id = ?", (minutes, currency, member_id)):
                    await conn.commit()
            self.starttime[key] = update_time
        print(f"Updated {user_count} users!") #TODO: future log entry!


    @update_member_points.before_loop
    async def before_update_member_points_task(self):
        print("Update users loop is waiting for the bot to load...") #TODO: future log entry
        await self.bot.wait_until_ready()


    ################################## Level Method ###############################################################

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
            async with db.execute(f"SELECT xp, vc_minutes, msg_count, user_id, (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.xp > t1.xp), (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.vc_minutes > t1.vc_minutes), (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.msg_count > t1.msg_count) AS pos FROM users AS t1 WHERE user_id = ?", (interaction.user.id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("You are not yet registered!", ephemeral=True)
                    return
    
        xp = result[0]
        vc_minutes = result[1]
        msg_count = result[2]
        xp_pos = result[4]
        vc_pos = result[5]
        msg_pos = result[6]
        lvl = self.get_level(xp)

        await interaction.response.send_message(f"You have **{xp}** XP ({xp_pos}. place), **{vc_minutes}** minute{'s' if vc_minutes!=1 else ''} in voice ({vc_pos}. place), written **{msg_count}** message{'s' if msg_count!=1 else ''} ({msg_pos}. place) and reached level {lvl}!")

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
                    desc += f"**{counter}.** <@{user_id}> - **{xp}** XP - **{msg_count}** message{'s' if msg_count!=1 else ''} - **{vc_minutes} ** minute{'s' if vc_minutes!=1 else ''} in voice - Level **{lvl}**\n **------------------------------------------------------------------**\n"
                    counter += 1
        
        confedembed = discord.Embed(title="Leaderboard", description=desc, color=discord.Color.blurple())

        confedembed.set_thumbnail(url=interaction.user.avatar.url)
        confedembed.set_footer(text=f"Requested by {interaction.user.name}")

        await interaction.response.send_message(embed=confedembed)



async def setup(bot):
    await bot.add_cog(LevelSystem(bot))