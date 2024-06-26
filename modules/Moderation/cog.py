import discord
from discord.ext import commands
from discord import app_commands
from utils import settings
import aiosqlite
import datetime

logger=settings.logging.getLogger("discord")

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "mod_sys.db"

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")


    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS WarnList (
                warn_id INTEGER PRIMARY KEY,
                mod_id INTEGER,
                guild_id INTEGER,
                user_id INTEGER,
                warns INTEGER DEFAULT 0,
                warn_reason TEXT,
                warn_time TEXT
                )
                """
            )

    
    ####################################################################################################################################
    ######################################################## Commands ##################################################################
    ####################################################################################################################################


    #Delete Messages Command TODO: fix bug if not enogh messages for member ir in channel, sends no embded
    # TODO: Allow channel selection!
    @app_commands.command(name="delete_messages", description="Delete some messages in a channel or from a member!")
    @app_commands.describe(number="The number of messages you want to delete?")
    @app_commands.describe(member="Whose messages you want to delete")
    @app_commands.describe(reason="Why is the member being kicked?")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete(self, interaction: discord.Interaction, number: int, member: discord.Member=None, reason: str=None):
        try:
            delete_counter = 0
            async for message in interaction.channel.history():
                if message.author == member or member is None:
                    await message.delete()
                    delete_counter += 1
                if delete_counter == number:
                    conf_embed = discord.Embed(title="**`✅` Success!**", color=discord.Color.red())
                    conf_embed.add_field(name="**Messages deleted!**", value=f"{number} messages will be removed!")
                    if reason is not None:
                        conf_embed.add_field(name="**Reason**", value=f"{reason}", inline=False) #if reason is not specified, dont include in embed
                    conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

                    await interaction.response.send_message(embed=conf_embed)
                    return
                    

        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"I am missing the permissions to delete messages ('manage messages').")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return


    ####################################################################################################################################
    ##################################################### Kick Command #################################################################
    ####################################################################################################################################

    #Kick Command
    @app_commands.command(name="kick", description="Kick a member!")
    @app_commands.describe(member="Who do you want to kick?")
    @app_commands.describe(reason="Why is the member being kicked?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"I am missing the permissions to kick {member.mention}.")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        conf_embed = discord.Embed(title="**`✅` Success!**", color=discord.Color.red())
        conf_embed.add_field(name="**Member kicked!**", value=f"{member.mention} has been kicked from the server!")
        if reason is not None:
            conf_embed.add_field(name="**Reason**", value=f"```{reason}```", inline=False) #if reason is not specified, dont include in embed
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)

        msg_embed= discord.Embed(title=f"**Kicked from {interaction.guild}**", color=discord.Color.red())
        if reason is not None:
            msg_embed.add_field(name="**Reason**", value=f"You were kicked from {interaction.guild} because of ```{reason}```", inline=False)
        try:
            await member.send(embed=msg_embed)
        except Exception as e:
            logger.info(f"Missing permission to send message to {member}!")
            logger.info(f"{e}")


    ####################################################################################################################################
    ##################################################### Ban Command ##################################################################
    ####################################################################################################################################

    
    @app_commands.command(name="ban", description="Ban a member!")
    @app_commands.describe(member="Who do you want to ban?")
    @app_commands.describe(reason="Why is the member being banned?")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"I am missing the permissions to ban {member.mention}.")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        conf_embed = discord.Embed(title="**`✅` Success!**", color=discord.Color.red())
        conf_embed.add_field(name="**Member banned!**", value=f"{member.mention} has been banned from the server!")
        if reason is not None:
            conf_embed.add_field(name="**Reason**", value=f"```{reason}```", inline=False) #if reason is not specified, dont include in embed
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)

        msg_embed= discord.Embed(title=f"**Banned from {interaction.guild}**", color=discord.Color.red())
        if reason is not None:
            msg_embed.add_field(name="**Reason**", value=f"You were banned from {interaction.guild} because of ```{reason}```", inline=False)
        try:
            await member.send(embed=msg_embed)
        except Exception as e:
            logger.info(f"Missing permission to send message to {member}!")
            logger.info(f"{e}")


    ####################################################################################################################################
    #################################################### Unban Command #################################################################
    ####################################################################################################################################


    @app_commands.command(name="unban", description="Unban a member!")
    @app_commands.describe(member="Who do you want to unban?")
    @app_commands.describe(reason="Why is the member being unbanned?")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        try:
            ban_entry = await interaction.guild.fetch_ban(member)
            await member.unban(ban_entry.user, reason=reason)
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"I am missing the permissions to unban {member.mention}.")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        conf_embed = discord.Embed(title="`✅` Success!", color=discord.Color.green())
        conf_embed.add_field(name="Member unbanned!", value=f"{member.mention} has been unbanned from the server!")
        if reason is not None:
            conf_embed.add_field(name="Reason", value=f"```{reason}```", inline=False) #if reason is not specified, dont include in embed
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)

        msg_embed= discord.Embed(title=f"**Unbanned from {interaction.guild}**", color=discord.Color.green())
        if reason is not None:
            msg_embed.add_field(name="**Reason**", value=f"You were unbanned from {interaction.guild} because of ```{reason}```", inline=False)
        try:
            await member.send(embed=msg_embed)
        except Exception as e:
            logger.info(f"Missing permission to send message to {member}!")
            logger.info(f"{e}")


    ####################################################################################################################################
    ##################################################### Warn Command #################################################################
    ####################################################################################################################################


    @app_commands.command(name="warn", description="Warn a user on the server")
    @app_commands.describe(member="Who do you want to warn?", reason="What reason is ther for warning the member?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self,
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str=None
        ):

        warn_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT INTO WarnList (user_id, guild_id, warns, warn_reason, mod_id, warn_time) VALUES (?, ?, ?, ?, ?, ?)",
                (member.id, interaction.guild.id, 1, reason, interaction.user.id, warn_time),
            )
            await db.commit()

            async with db.execute(
                "SELECT warn_id FROM WarnList WHERE user_id = ? AND guild_id = ? ORDER BY warn_id DESC LIMIT 1",
                (member.id, interaction.guild.id),
            ) as cursor:
                row = await cursor.fetchone()
                warn_id = row[0]
                
        warnUser_embed = discord.Embed(
            title="`⚠️` Warning",
            description=f"You have received a warning in **{interaction.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        warnUser_embed.add_field(name="Moderator:", value=f"```{interaction.user}```", inline=False)
        warnUser_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        warnUser_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        warnUser_embed.set_author(name=f"{interaction.guild.name}", icon_url=member.avatar)
        warnUser_embed.set_thumbnail(url=member.avatar)
        warnUser_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)
        
        warn_embed = discord.Embed(
            title="`✅` Warn",
            description=f"You have warned {member.mention} in **{interaction.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        warn_embed.add_field(name="Moderator:", value=f"```{interaction.user}```", inline=False)
        warn_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        warn_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        warn_embed.set_author(name=f"{interaction.guild.name}", icon_url=interaction.user.avatar.url)
        warn_embed.set_thumbnail(url=member.avatar)
        warn_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)
        
        await member.send(embed=warnUser_embed)
        await interaction.response.send_message(embed=warn_embed, ephemeral=False)


    ####################################################################################################################################
    #################################################### Unwarn Command ################################################################
    ####################################################################################################################################

    @app_commands.command(name="unwarn", description="Remove a warning from a user on the server")
    @app_commands.describe(member="Who do you want to unwarn?", reason="What reason is there for removing the warning of the member?", warn_id="The warning withh which id is to be removed?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def unwarn(
        self,
        interaction: discord.Interaction, 
        member: discord.Member,
        warn_id: int, 
        reason: str=None
        ):
        
        unwarnUser_embed = discord.Embed(
            title="`🍀` Unwarn",
            description=f"A warn in **{interaction.guild.name}** has been removed.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unwarnUser_embed.add_field(name="Moderator:", value=f"```{interaction.user}```", inline=False)
        unwarnUser_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        unwarnUser_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        unwarnUser_embed.set_author(name=f"{interaction.guild.name}", icon_url=self.bot.user.avatar)
        unwarnUser_embed.set_thumbnail(url=interaction.guild.icon)
        unwarnUser_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)
        
        unwarn_embed = discord.Embed(
            title=f"`✅` Unwarn",
            description=f"You have removed a warning for {member.mention} in **{interaction.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unwarn_embed.add_field(name="Moderator:", value=f"```{interaction.user}```", inline=False)
        unwarn_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        unwarn_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        unwarn_embed.set_author(name=f"{interaction.guild.name}", icon_url=self.bot.user.avatar)
        unwarn_embed.set_thumbnail(url=member.avatar)
        unwarn_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)
        
        
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "DELETE FROM WarnList WHERE user_id = ? AND guild_id = ? AND warn_id = ?",
                (member.id, interaction.guild.id, warn_id)
            )
            await db.commit()
 
        await member.send(embed=unwarnUser_embed)
        await interaction.response.send_message(embed=unwarn_embed, ephemeral=False)


    ####################################################################################################################################
    ############################################# Remove all warnings Command ##########################################################
    ####################################################################################################################################

    @app_commands.command(name="unwarn_all", description="Remove all warnings from a user on the server")
    @app_commands.describe(member="Who do you want to unwarn?", reason="What reason is there for removing all warnings of the member?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def unwarn_all(
        self,
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: str=None
        ):
        
        unwarnUser_embed = discord.Embed(
            title="`🍀` Unwarn",
            description=f"All your warnings in **{interaction.guild.name}** have been removed.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unwarnUser_embed.add_field(name="Moderator:", value=f"```{interaction.user}```", inline=False)
        unwarnUser_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        unwarnUser_embed.set_author(name=f"{interaction.guild.name}", icon_url=self.bot.user.avatar)
        unwarnUser_embed.set_thumbnail(url=interaction.guild.icon)
        unwarnUser_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)
        
        unwarn_embed = discord.Embed(
            title=f"`✅` Unwarn",
            description=f"You have removed all warnings for {member.mention} in **{interaction.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unwarn_embed.add_field(name="Moderator:", value=f"```{interaction.user}```", inline=False)
        unwarn_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        unwarn_embed.set_author(name=f"{interaction.guild.name}", icon_url=self.bot.user.avatar)
        unwarn_embed.set_thumbnail(url=member.avatar)
        unwarn_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)
        
        
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "DELETE FROM WarnList WHERE user_id = ? AND guild_id = ?",
                (member.id, interaction.guild.id)
            )
            await db.commit()
 
        await member.send(embed=unwarnUser_embed)
        await interaction.response.send_message(embed=unwarn_embed, ephemeral=False)


    ####################################################################################################################################
    ############################################### Show all warnings Command ##########################################################
    ####################################################################################################################################


    @app_commands.command(name="list_warns", description="Shows all warnings of a user on the server")
    @app_commands.describe(member="Whose warnings do you want to display?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):

        warns_info = []
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT warn_id, mod_id, guild_id, user_id, warns, warn_reason, warn_time FROM WarnList WHERE user_id = ? AND guild_id = ?", (member.id, interaction.guild.id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    warn_id, mod_id, guild_id, user_id, warns, warn_reason, warn_time = row
                    warn_time = datetime.datetime.strptime(warn_time, '%Y-%m-%d %H:%M:%S')
                    warns_info.append(f"**Warn-ID:** __{warn_id}__ | **Warn issued at:** {warn_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    warns_info.append(f"**Moderator:** <@{mod_id}> | **Mod-ID**: __{mod_id}__\n")
                    warns_info.append(f"**> Reason:**\n```{warn_reason}```")
                    warns_info.append("\n")

        if not warns_info:
            warnings_embed = discord.Embed(
                title="`⚠️` The user has no warns!",
                description=f"User: {member.mention}",
                color=discord.Color.red(),
            )
        else:
            warnings_embed = discord.Embed(
                title=f"`⚠️` Warning List for {member.name}#{member.discriminator}",
                description=f"__**List of Warnings**__",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
        warnings_embed.add_field(name="", value="".join(warns_info), inline=False)
        warnings_embed.set_author(name=f"{interaction.guild.name}", icon_url=interaction.guild.icon)
        warnings_embed.set_thumbnail(url=member.avatar)
        warnings_embed.set_footer(text=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar)

        await interaction.response.send_message(embed=warnings_embed, ephemeral=False)


    ####################################################################################################################################
    ################################################# Error Handeling! #################################################################
    ####################################################################################################################################



    #On command error
    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"Following error has occured: ```{error}```")
        raise error


    #Delete error, when user lacks permissions
    @delete.error
    async def delete_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to delete messages!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    #Kick error, when user lacks permissions
    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to kick a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


    #Ban error, when user lacks permissions
    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to ban a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    
    #Unban error, when user lacks permissions
    @unban.error
    async def unban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to unban a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    
    #warn error, when user lacks permissions
    @warn.error
    async def warn_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to warn a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


    #Unwarn error, when user lacks permissions
    @unwarn.error
    async def unwarn_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to unwarn a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


    #Unwarn all error, when user lacks permissions
    @unwarn_all.error
    async def unwarn_all_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to remove all warnings from a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


    #Warnings error, when user lacks permissions
    @warnings.error
    async def warnings_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to list the warnings of a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Moderation(bot))