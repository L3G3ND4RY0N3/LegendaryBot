from constants.enums import ActivityStats
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice
import random
import math
import aiosqlite
import datetime
from utils import settings, guildjsonfunctions
from utils.Activity.activity_helpers import update_all_members_in_voice
from utils.customwrappers import is_owner
from utils.dbhelpers.activity_db_helpers import display_test, get_user_stats_with_position, handle_activity_update, handle_leaderboard_command, handle_stats_command
from utils.dbhelpers.migrate_from_old_db import migrate_db_data
from utils.embeds.activity_embeds import activity_stats_embed, guild_leaderboard_embed
from utils.embeds.embedbuilder import forbidden_embed, success_embed, warn_embed
from utils.structs.activity_times_data import SessionManager


logger=settings.logging.getLogger("discord")

class LevelSystem(commands.Cog, name="LevelSystem"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.DB = "level.db"
        self.users_in_voice = SessionManager()
        self.guild_count = 0 # number of guilds the bot is in TODO: reverse assignment
        self.vc_count = 0 # number of voice channels the bot has acces to TODO: reverse assignment
        self.new_users = 0 # count of users who get added to the start time dict, when the bot is booted
        self.update_member_points.start() # starts the update_member_points task
        self.check_members_in_voice.start() # starts the check_members_in_voice task


    def cog_unload(self):
        self.update_member_points.cancel()
        self.check_members_in_voice.cancel()
        

#region EVENTS
    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")

    # OBSOLETE TODO: Remove, since it should always return after the first check, since the guild id will not be in activity ids set?
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """checks on guild join all members in a vc"""
        if guild.id not in guildjsonfunctions.ACTIVITY_IDS:
            return
        vc_count = len(guild.voice_channels)
        self.guild_count += 1
        new_user_count = 0
        for vc in guild.voice_channels:
            for member in vc.members:
                if member.id not in self.users_in_voice.sessions.keys():
                    new_user_count+=1
                    self.users_in_voice.add_session(member_id=member.id, guild_id=guild.id)
        self.vc_count += vc_count
        self.new_users += new_user_count
        logger.info(f"Checked {vc_count} voice channel{'s' if vc_count!=1 else ''} in {guild.name} and added {new_user_count} user{'s' if new_user_count!=1 else ''}!")
#endregion


    ##################################### Tasks #################################################################
    #region TASKS
    @tasks.loop(minutes=1, count=2)
    async def check_members_in_voice(self):
        """runs after the bot starts to add all members currently in a voice channel to the SessionManager so that they get points"""
        guilds = self.bot.guilds
        vc_channels: list[discord.VoiceChannel] = []
        for guild in guilds: #TODO: here and in on_message, on_voice_state_update guild_id match against activity_ids, then the starttime dict should only hold members in guilds with active tracking
            if guild.id not in guildjsonfunctions.ACTIVITY_IDS:
                continue
            vc_channels.extend(guild.voice_channels)
        vc_channels_count = len(vc_channels)
        new_user_count = 0
        for channel in vc_channels:
            for member in channel.members:
                if member.id not in self.users_in_voice.sessions.keys():
                    new_user_count += 1
                    self.users_in_voice.add_session(member_id=member.id, guild_id=member.guild.id)
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

    
    @tasks.loop(minutes=1)
    async def update_member_points(self):
        """regularly updates the points of all members currently in a voice channel"""
        if not bool(self.users_in_voice.sessions):
            logger.info("No members currently in a voice channel!") 
            return
        user_count = update_all_members_in_voice(self.users_in_voice, self.bot)
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
        if message.author.bot or message.guild.id not in guildjsonfunctions.ACTIVITY_IDS:
            return

        xp = random.randint(5,15)
        handle_activity_update(message.author, messages=1, xp=xp)

    ########################## Voice Tracker #######################################################

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if  member.bot or member.guild.id not in guildjsonfunctions.ACTIVITY_IDS:
            return
        if before.channel is None and after.channel is not None:
            self.users_in_voice.add_session(member.id, member.guild.id)
        elif before.channel is not None and after.channel is None:
            if not (session := self.users_in_voice.remove_session(member.id)):
                return
            end = datetime.datetime.now()
            duration = end - session.start_time
            minutes = int(duration.total_seconds() / 60)
            currency = minutes * 20  # TODO: Customize how much currency to award per minute
            handle_activity_update(member, minutes=minutes, xp=currency)
        # user switched guilds
        elif before.channel.guild.id != after.channel.guild.id:
            self.users_in_voice.update_session(member_id=member.id, guild_id=after.channel.guild.id)
    #endregion

#region COMMANDS

    ########################## Stats Command ###################################################
    @app_commands.command(name="activity_stats", description="Look up your activity stats")
    async def activity_stats(self, ctx: discord.Interaction) -> None:
        activity_stats = handle_stats_command(ctx.user)
        emb = activity_stats_embed(activity_stats, ctx.user)
        # emb = discord.Embed(color=discord.Color.blue(), title=f"{ctx.user.global_name}´s Activity Statistics")
        # TODO: Make readabel e.g. using an Enum  
        # for key, val in activity_stats.items():
        #     emb.add_field(name=f"{key}", value=f"{val}", inline=False)
        await ctx.response.send_message(embed=emb)


    ########################## Leaderboard Command #######################################################

    @app_commands.command(name="leaderboard", description="Look at the leaderborad!")
    @app_commands.describe(stat="the stat for which you want the leaderboard to be ordered by")
    @app_commands.choices(stat = [
        Choice(name=stat.name.title(), value=stat.value) for stat in ActivityStats
    ])
    async def leaderboard(self, interaction: discord.Interaction, stat: str = ActivityStats.XP.value, guild_only: bool = True):
        table = handle_leaderboard_command(interaction.user, stat, guild_only=guild_only)
        if table == "":
            # TODO: create a better embed maybe!
            emb = warn_embed(f"There is currently no leaderboard available for {interaction.user.guild.name}")
        else:
            emb = guild_leaderboard_embed(table, stat, interaction.user)

        await interaction.response.send_message(embed=emb)
#endregion

#region DEBUG COMMANDS
    @is_owner()
    @app_commands.command(name="display_member_info", description="Look at infos")
    async def display(self, ctx: discord.Interaction) -> None:
        await ctx.response.send_message(content=display_test(ctx.user))

    
    @is_owner()
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


    # TODO: recreate with new models
    @is_owner()
    @app_commands.command(name="rank", description="Check your current rank!")
    async def rank(self, interaction: discord.Interaction):
        # user_id = interaction.user.id
        # async with aiosqlite.connect(self.DB) as db:
        #     async with db.execute(f"SELECT xp, vc_minutes, msg_count, user_id, (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.xp > t1.xp), (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.vc_minutes > t1.vc_minutes), (SELECT COUNT(*) + 1 FROM users AS t2 WHERE t2.msg_count > t1.msg_count) AS pos FROM users AS t1 WHERE user_id = ?", (user_id,)) as cursor:
        #         result = await cursor.fetchone()
        #         if result is None:
        #             await interaction.response.send_message("You are not yet registered!", ephemeral=True)
        #             return
    
        # xp = result[0]
        # vc_minutes = result[1]
        # msg_count = result[2]
        # xp_pos = result[4]
        # vc_pos = result[5]
        # msg_pos = result[6]
        # lvl = self.get_level(xp)

        formated_str = get_user_stats_with_position(interaction.user)

        #await interaction.response.send_message(f"{'You' if user is None else user.mention} {'have' if user is None else 'has'} **{xp}** XP ({xp_pos}. place), **{vc_minutes}** minute{'s' if vc_minutes!=1 else ''} in voice ({vc_pos}. place), written **{msg_count}** message{'s' if msg_count!=1 else ''} ({msg_pos}. place) and reached level {lvl}!")
        await interaction.response.send_message(formated_str)


#endregion

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))