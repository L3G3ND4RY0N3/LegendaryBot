import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice
import random
import math
import aiosqlite
import datetime
from utils import settings, guildjsonfunctions
from utils.customwrappers import is_owner
from utils.dbhelpers.activity_db_helpers import display_test, handle_activity_update, handle_guild_leaderboard, handle_stats_command
from utils.dbhelpers.migrate_from_old_db import migrate_db_data
from utils.embeds.activity_embeds import activity_stats_embed, guild_leaderboard_embed
from utils.embeds.embedbuilder import forbidden_embed, success_embed


logger=settings.logging.getLogger("discord")

class LevelSystem(commands.Cog, name="LevelSystem"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.DB = "level.db" # TODO: have some sort of server dependent tracking either trough relational databases or something else.
        self.starttime = {} # initiates a  dict for keeping "user": "starttime" with starttime being the time they joined a voice channel or got updated
        self.guild_count = 0 # number of guilds the bot is in TODO: reverse assignment
        self.vc_count = 0 # number of voice channels the bot has acces to TODO: reverse assignment
        self.new_users = 0 # count of users who get added to the start time dict, when the bot is booted
        self.update_member_points.start() # starts the update_member_points task
        self.check_members_in_voice.start() # starts the check_members_in_voice task


    def cog_unload(self):
        self.update_member_points.cancel()

    def cog_unload(self):
        self.check_members_in_voice.cancel()

#region EVENTS
    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")   
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

    # OBSOLETE TODO: Remove?
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """checks on guild join all members in a vc"""
        if guild.id not in guildjsonfunctions.activity_ids:
            return
        vc_count = len(guild.voice_channels)
        self.guild_count += 1
        new_user_count = 0
        for vc in guild.voice_channels:
            for member in vc.members:
                if member.id not in self.starttime.keys():
                    new_user_count+=1
                    self.starttime[member.id] = datetime.datetime.now()
        self.vc_count += vc_count
        self.new_users += new_user_count
        logger.info(f"Checked {vc_count} voice channel{'s' if vc_count!=1 else ''} in {guild.name} and added {new_user_count} user{'s' if new_user_count!=1 else ''}!")
#endregion


    ##################################### Tasks #################################################################
    #region TASKS
    @tasks.loop(minutes=1, count=2)
    async def check_members_in_voice(self):
        guilds = self.bot.guilds
        vc_channels = []
        for guild in guilds: #TODO: here and in on_message, on_voice_state_update guild_id match against activity_ids, then the starttime dict should only hold members in guilds with active tracking
            if guild.id not in guildjsonfunctions.activity_ids:
                continue
            for vc_channel in guild.voice_channels:
                vc_channels.append(vc_channel)
        vc_channels_count = len(vc_channels)
        new_user_count = 0
        for channel in vc_channels:
            for member in channel.members:
                if member.id not in self.starttime.keys():
                    new_user_count+=1
                    self.starttime[member.id] = datetime.datetime.now()
        self.vc_count = vc_channels_count # TODO: buggy, for += it adds the vc_count giving double result! fix with .current_loop conditional?
        self.guild_count = len(guilds)
        self.new_users += new_user_count
        logger.info(f"Checked {vc_channels_count} voice channel{'s' if vc_channels_count!=1 else ''} across {self.guild_count} server{'s' if self.guild_count!=1 else ''} and registered times for {new_user_count} user{'s' if new_user_count!=1 else ''}!") 

    @check_members_in_voice.before_loop
    async def before_check_members_in_voice_task(self):
        logger.info("Check user loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()

    @check_members_in_voice.after_loop
    async def after_check_members_in_voice(self):
        logger.info(f"Checked {self.vc_count} voice channel{'s' if self.vc_count!=1 else ''} across {self.guild_count} server{'s' if self.guild_count!=1 else ''} and added a total of {self.new_users} member{'s' if self.new_users!=1 else ''}!")
        logger.info("Ending check member loop!")


    @tasks.loop(minutes=5)
    async def update_member_points(self):
        if not bool(self.starttime):
            logger.info("No members currently in a voice channel!") 
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
        logger.info(f"Updated points and times for {user_count} user{'s' if user_count!=1 else ''}!") 


    @update_member_points.before_loop
    async def before_update_member_points_task(self):
        logger.info("Update users loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()
    #endregion

    #region STATIC METHODS
    ################################## Level Method ###############################################################

    @staticmethod
    def get_level(xp):
        lvl = 1

        while True:
            if xp >= math.ceil((6 * (lvl ** 4))/2.5):
                lvl += 1
            else:
                return lvl
            
    ################################## time method #####################################################
            
    @staticmethod
    def calc_time(time_in_minutes):
        if time_in_minutes < 60:
            return time_in_minutes
        else:
            return time_in_minutes//60
    #endregion
            
    #region EVENTS
    ########################## Message Tracker #######################################################

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild.id not in guildjsonfunctions.activity_ids:
            return

        xp = random.randint(5,15)
        handle_activity_update(message.author, messages=1,xp=xp)
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
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.guild.id not in guildjsonfunctions.activity_ids:
            return
        if before.channel is None and after.channel is not None:
            # User joined a voice channel
            start = datetime.datetime.now()
            self.starttime[member.id] = start
            # logger.info(f"{member.name} joined voice channel {after.channel.name} in {member.guild.name}")
        elif before.channel is not None and after.channel is None:
            # User left a voice channel
            # logger.info(f"{member.name} left voice channel {before.channel.name} in {member.guild.name}")
            # Calculate voice activity duration
            end = datetime.datetime.now()
            duration = end - self.starttime.pop(member.id, end)
            minutes = int(duration.total_seconds() / 60)
            # Award currency for unmuted time
            currency = minutes*20  # TODO: Customize how much currency to award per minute
            # Update currency in the database
            handle_activity_update(member, minutes, xp=currency)
            async with aiosqlite.connect(self.DB) as conn:
                async with conn.execute("UPDATE users SET vc_minutes = vc_minutes + ?, xp = xp + ? WHERE user_id = ?", (minutes, currency, member.id)):
                    await conn.commit()
        # elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        #     # User switched voice channels
        #     logger.info(f"{member.name} switched from voice channel {before.channel.name} to {after.channel.name} in {member.guild.name}")
    #endregion

#region COMMANDS
    ########################## Rank Command #######################################################

    @app_commands.command(name="rank", description="Check your current rank!")
    @app_commands.describe(user="user you want to check the rank off, default is yourself")
    async def rank(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user_id = interaction.user.id
        else:
            user_id = user.id
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(f"SELECT xp, vc_minutes, msg_count, user_id, (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.xp > t1.xp), (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.vc_minutes > t1.vc_minutes), (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.msg_count > t1.msg_count) AS pos FROM users AS t1 WHERE user_id = ?", (user_id,)) as cursor:
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

        await interaction.response.send_message(f"{'You' if user is None else user.mention} {'have' if user is None else 'has'} **{xp}** XP ({xp_pos}. place), **{vc_minutes}** minute{'s' if vc_minutes!=1 else ''} in voice ({vc_pos}. place), written **{msg_count}** message{'s' if msg_count!=1 else ''} ({msg_pos}. place) and reached level {lvl}!")


    ########################## Leaderboard Command #######################################################

    @app_commands.command(name="leaderboard", description="Look at the leaderborad!")
    @app_commands.describe(stat="the stat for which you want the leaderboard to be ordered by")
    @app_commands.choices(stat = [
        Choice(name = "message count", value = "msg_count"),
        Choice(name = "minutes in voice", value = "vc_minutes")
    ])
    async def leaderboard(self, interaction: discord.Interaction, stat: str = None):
        if not stat:
            order = 'xp'
        else:
            order = stat
        desc=""
        counter = 1
        con_string = f"SELECT user_id, xp, msg_count, vc_minutes FROM users WHERE {order} > 0 ORDER BY {order} DESC LIMIT 10"
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(
                con_string
            ) as cursor:
                async for user_id, xp, msg_count, vc_minutes in cursor:
                    lvl = self.get_level(xp)
                    time = self.calc_time(vc_minutes)
                    user = discord.Client.get_user(self.bot, int(user_id))
                    if user is not None:                        
                        # TODO: Fix formatting of leaderboard
                        desc += f"**{counter:<2}.** {user.mention:32} - **{xp:<9}** XP - **{msg_count:<5}** message{'s' if msg_count!=1 else ''} - **{time:<4} ** {'minute' if vc_minutes<60 else 'hour'}{'s' if vc_minutes!=1 else ''} in voice - Level **{lvl:<3}**\n **------------------------------------------------------------------**\n"
                        counter += 1
                    else:
                        #TODO: delete user from db or set as inactive (and fetch new TOP 10?)
                        continue
        
        table = handle_guild_leaderboard(interaction.user, order)
        emb = guild_leaderboard_embed(table, order, interaction.user)
        # confedembed = discord.Embed(title="Leaderboard", description=desc, color=discord.Color.blurple())

        # confedembed.set_thumbnail(url=interaction.user.avatar.url)
        # confedembed.set_footer(text=f"Requested by {interaction.user.name}, leaderboard sorted by {order}")


        await interaction.response.send_message(embed=emb)
#endregion

#region DEBUG COMMANDS
    @is_owner()
    @app_commands.command(name="display_member_info", description="Look at infos")
    async def display(self, ctx: discord.Interaction) -> None:
        await ctx.response.send_message(content=display_test(ctx.user))

    @is_owner()
    @app_commands.command(name="activity_stats", description="Look up your activity stats")
    async def activity_stats(self, ctx: discord.Interaction) -> None:
        activity_stats = handle_stats_command(ctx.user)
        emb = activity_stats_embed(activity_stats, ctx.user)
        # emb = discord.Embed(color=discord.Color.blue(), title=f"{ctx.user.global_name}´s Activity Statistics")
        # TODO: Make readabel e.g. using an Enum  
        # for key, val in activity_stats.items():
        #     emb.add_field(name=f"{key}", value=f"{val}", inline=False)
        await ctx.response.send_message(embed=emb)

    
    is_owner()
    @app_commands.command(name="migrate_activity_data", description="Migrate data from old sqlite db to new ORM")
    async def migrate_data_for_activity(self, ctx: discord.Interaction) -> None:
        con_str = "SELECT user_id, xp, msg_count, vc_minutes FROM users"
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(con_str) as cursor:
                result = await cursor.fetchall()
        if not migrate_db_data(self.bot, result):
            await ctx.response.send_message(embed=forbidden_embed("Failure to migrate database!"))
            return
        await ctx.response.send_message(embed=success_embed("Successfully migrated data!"))


#endregion

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))