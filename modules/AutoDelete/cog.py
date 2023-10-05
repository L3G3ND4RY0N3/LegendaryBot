import discord
from discord.ext import commands
from discord import app_commands
from utils import settings
import asyncio
import sqlite3

logger=settings.logging.getLogger("discord")


class Autodelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autodelete_channels = []

        self.create_db()


    ####################################################################################################################################
    ######################################################### Listener #################################################################
    ####################################################################################################################################

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()
        logger.info("Autodelete.py is ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        for channel_id, time, max_msg_count, _ in self.autodelete_channels:
            if message.channel.id != channel_id:
                continue
            
            if max_msg_count != None:
                messages = [message async for message in message.channel.history(limit=100)]
                channel_msg_count = len(messages)

                if (not message.pinned
                    and max_msg_count<channel_msg_count):
                    await asyncio.sleep(time)
                    await message.delete()
                    return

            elif (not message.pinned):
                await asyncio.sleep(time)
                await message.delete()
                return

            else:
                return
            
    
    ####################################################################################################################################
    ##################################################### DB Functions #################################################################
    ####################################################################################################################################

    def create_db(self):
        conn = sqlite3.connect("tables/autodelete.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS autodelete_settings (channel_id INTEGER, time INTEGER, max_msg_count INTEGER, guild_id INTEGER)")
        conn.commit()
        conn.close()

    def save_settings(self):
        conn = sqlite3.connect("tables/autodelete.db")
        c = conn.cursor()
        c.execute("DELETE FROM autodelete_settings")
        for channel_id, time, max_msg, guild_id in self.autodelete_channels:
            c.execute("INSERT INTO autodelete_settings VALUES (?, ?, ?, ?)", (channel_id, time, max_msg, guild_id))
        conn.commit()
        conn.close()

    def load_settings(self):
        conn = sqlite3.connect("tables/autodelete.db")
        c = conn.cursor()
        c.execute("SELECT * FROM autodelete_settings")
        results = c.fetchall()
        self.autodelete_channels = results
        conn.close()

    def remove_channel_from_db(self, channel_id):
        conn = sqlite3.connect("tables/autodelete.db")
        c = conn.cursor()
        c.execute("DELETE FROM autodelete_settings WHERE channel_id=?", (channel_id,))
        conn.commit()
        conn.close()

    def remove_all_channel_for_guild_from_db(self, guild_id):
        conn = sqlite3.connect("tables/autodelete.db")
        c = conn.cursor()
        c.execute("DELETE FROM autodelete_settings WHERE guild_id=?", (guild_id,))
        conn.commit()
        conn.close()

    def get_autodelete_channels(self):
        autodelete_channel_ids = [channel_id for channel_id, _, _, _ in self.autodelete_channels]
        autodelete_channels = [self.bot.get_channel(channel_id) for channel_id in autodelete_channel_ids]
        return autodelete_channels
    
    
    ####################################################################################################################################
    ##################################################### Add Command ##################################################################
    ####################################################################################################################################

    @app_commands.command(name="add_autodelete_channel", description="Add autodelete mode to a channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(time = "Set the time after which messages in the channel will be deleted!", 
                           channel="Select the channel to delete messages in", 
                           max_msg_count="Select the max amount of messages in the channel before deleting")
    async def autodelset(self, ctx:discord.Interaction, time: int, channel: discord.TextChannel, max_msg_count: int = None):
        if channel in self.get_autodelete_channels():
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"{channel.mention} is already an autodelete channel!",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            await ctx.response.send_message(embed=embed, file=file)
            return
        if max_msg_count != None:
            self.autodelete_channels.append((channel.id, time, max_msg_count, ctx.guild.id))
        else:
            self.autodelete_channels.append((channel.id, time, None, ctx.guild.id))
        self.save_settings()

        if max_msg_count != None:
            embed = discord.Embed(
            title="`💣` | Autodelete Settings",
            description=f"Added autodelete to {channel.mention}, deleting messages after {time} seconds and {max_msg_count} messages are reached!.",
            color=discord.Color.red()
        )
            
        else:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"Added autodelete to {channel.mention}, deleting messages after {time} seconds.",
                color=discord.Color.red()
            )
        file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
        embed.set_thumbnail(url="attachment://Trash-Can.png")
        embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

        await ctx.response.send_message(embed=embed, file=file)


    ####################################################################################################################################
    #################################################### Remove Command ################################################################
    ####################################################################################################################################

    @app_commands.command(name="remove_autodelete_channel", description="Remove the autodelete function from a channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Select the channel to remove the autodelete from")
    async def autodelremove(self, ctx:discord.Interaction, channel: discord.TextChannel):
        if channel.id not in [channel_id for channel_id, _, _, _ in self.autodelete_channels]:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"{channel.mention} did not have autodelete enabled!",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            await ctx.response.send_message(embed=embed, file=file)
            return

        removed_channels = []
        for i, (channel_id, time, max_msg_count, _) in enumerate(self.autodelete_channels):
            if channel.id == channel_id:
                removed_channels.append((channel, time, max_msg_count))
                self.autodelete_channels.pop(i)
                self.remove_channel_from_db(channel_id)
                break
        self.save_settings()

        if removed_channels:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"Autodelete function was removed for {channel.mention}.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            for channel, time, max_msg_count in removed_channels:
                embed.add_field(name="Channel / Time/ Max Messages", value=f"{channel.mention} / {time} / {max_msg_count}", inline=True)
            await ctx.response.send_message(embed=embed, file=file)
        else:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"{channel.mention} did not have autodelete enabled!",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            await ctx.response.send_message(embed=embed, file=file)


    ####################################################################################################################################
    ################################################## Remove all Command ##############################################################
    ####################################################################################################################################

    @app_commands.command(name="remove_all_autodelete_channel", description="Remove the autodelete function from a channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def autodelremove_all(self, ctx:discord.Interaction):
        s_guild_id = ctx.guild.id
        if s_guild_id not in [guild_id for _, _, _, guild_id in self.autodelete_channels]:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"{ctx.guild.name} did not have channels with autodelete enabled!",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            await ctx.response.send_message(embed=embed, file=file)
            return
        
        else:
            # removed_autodelete_channels = [guild_id for _, _, _, guild_id in self.autodelete_channels if guild_id == s_guild_id]
            # for guild_id in removed_autodelete_channels:
            #     self.autodelete_channels.remove()         
            self.autodelete_channels = [(channel_id, time, max_msg, guild_id) for (channel_id, time, max_msg, guild_id) in self.autodelete_channels if guild_id != s_guild_id]          
            self.remove_all_channel_for_guild_from_db(s_guild_id)
            self.save_settings()
    
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"Autodelete function was removed for all channels in {ctx.guild.name}.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            await ctx.response.send_message(embed=embed, file=file)

            
    ####################################################################################################################################
    #################################################### List Command ##################################################################
    ####################################################################################################################################

    @app_commands.command(name="list_autodelete_channel", description="Show all channels with the autodelete function enabled")
    @app_commands.checks.has_permissions(administrator=True)
    async def autodelcheck(self, ctx:discord.Interaction):
        autodelete_channels = self.get_autodelete_channels()
        if ctx.guild.id in [guild_id for _, _, _, guild_id in self.autodelete_channels]:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description="Active autodelete channels:",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            for channel_id, time, max_msg_count, guild_id in self.autodelete_channels:
                channel = self.bot.get_channel(channel_id)
                if channel is not None and guild_id == ctx.guild.id:
                    embed.add_field(name="Channel / Time / Max Messages", value=f"{channel.mention} / {time} sec. / {max_msg_count}", inline=True)
                    file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
                    embed.set_thumbnail(url="attachment://Trash-Can.png")
                    embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)
            await ctx.response.send_message(embed=embed, file=file)
        else:
            embed = discord.Embed(
                title="`💣` | Autodelete Settings",
                description=f"No channels with autodelete function registered for **{ctx.guild.name}**!",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Trash-Can.png", filename="Trash-Can.png")
            embed.set_thumbnail(url="attachment://Trash-Can.png")
            embed.set_footer(text=f"{ctx.guild.name} | Action taken by {ctx.user}", icon_url=self.bot.user.avatar)

            await ctx.response.send_message(embed=embed, file=file)


    ####################################################################################################################################
    ################################################# Error Handeling! #################################################################
    ####################################################################################################################################

    @autodelset.error
    async def autodelset_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to add autodelete channels!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    
    @autodelremove.error
    async def autodelremove_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to remove autodelete channels!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    
    @autodelremove_all.error
    async def autodelremove_all_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to remove autodelete channels!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


    @autodelcheck.error
    async def autodelcheck_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to list autodelete channels!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Autodelete(bot))