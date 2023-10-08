from typing import Any, Coroutine
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import settings, jsonfunctions
import json

logger=settings.logging.getLogger("discord")

class TemporaryVoice(commands.Cog, name="TemporaryVoice"):
    def __init__(self, bot):
        self.bot = bot
        self.temporary_voice_channels = []
        self.check_temp_vc.start()

    def cog_unload(self):
        self.check_temp_vc.cancel()


    ####################################################################################################################################
    ######################################################### Listener #################################################################
    ####################################################################################################################################

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("TemporaryVoice.py is ready!")   


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r") as f:
            data = json.load(f)

        guild_id = str(member.guild.id)

        if guild_id not in data:
            return

        if after.channel:
            vc_id = str(after.channel.id)

            temp_vc_list = list(data[guild_id].values())

            temp_vc_channel_name = f"{member.name}'s voice"

            if vc_id in temp_vc_list:
                temp_channel = await after.channel.clone(name=temp_vc_channel_name)
                await member.move_to(temp_channel)
                self.temporary_voice_channels.append(temp_channel.id)
        
        if before.channel: 
            if before.channel.id in self.temporary_voice_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()

    # delete the channel from the json, when it gets deleted not using the command
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if type(channel) == discord.TextChannel:
            return
        
        guild_id, channel_id, cat_id = str(channel.guild.id), str(channel.id), str(channel.category.id)

        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r+") as f:
            data = json.load(f)

            if guild_id not in data:
                return

            channel_ids = list(data[guild_id].values())

            if channel_id in channel_ids:
                try:
                    data[guild_id].pop(cat_id)

                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)

                except KeyError:
                    logger.info(f"{channel.name} in {channel.guild.name} was not a temporary voice channel")
                    return
                
            else:
                logger.info(f"{channel.name} in {channel.guild.name} was not a temporary voice channel")


    # Temp Voice Channels für Multiple Server from Json File
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r") as f:
            data = json.load(f)
        
        data[str(guild.id)] = {}
                    
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "w") as f:
            json.dump(data, f, indent=4)

    # Deletes the temporary voice channels for a server if the bot gets kicked or banned from the server (guild)
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r") as f:
            data = json.load(f)
        
        data.pop(str(guild.id))

        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "w") as f:
            json.dump(data, f, indent=4)


    ####################################################################################################################################
    ######################################################### Tasks ####################################################################
    ####################################################################################################################################

    @tasks.loop(minutes=1, count=1)
    async def check_temp_vc(self):
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r") as f:
            data = json.load(f)
        guilds = self.bot.guilds
        guild_count = len(guilds)
        vc_channels = []
        count_deleted = 0
        for guild in guilds:
            guild_id = str(guild.id)
            if guild_id not in data:
                    continue
            for vc_channel in guild.voice_channels:

                if vc_channel.id in list(data[guild_id].values()):
                    vc_channels.append(vc_channel)

                else:
                    with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r+") as f:
                        data = json.load(f)
                        cat_id = str(vc_channel.category_id)
                        data[guild_id].pop(cat_id)
                        f.seek(0)
                        f.truncate()
                        count_deleted += 1
                        json.dump(data, f, indent=4)

        vc_channels_count = len(vc_channels)
        logger.info(f"Checked {vc_channels_count} temporary voice channel{'s' if vc_channels_count!=1 else ''} across {guild_count} server{'s' if guild_count!=1 else ''} and registered {count_deleted} deleted temporary voice channels!") 


    @check_temp_vc.before_loop
    async def before_check_members_in_voice_task(self):
        logger.info("Check temp_vc loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()


    @check_temp_vc.after_loop
    async def after_check_members_in_voice(self):
        logger.info(f"Finished check temp_vc loop!")
        logger.info("Ending check temporary voice channel loop!")


    ####################################################################################################################################
    ##################################################### Add Command ##################################################################
    ####################################################################################################################################

    @app_commands.command(name="create_temp_voice_channel", description="create a temporary voice channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(category="select the category to create temporary voice channel in",
                           name="select the name for the channel (default: join to create)")
    async def add_temp_voice_channel(self, ctx:discord.Interaction, category:discord.CategoryChannel, name: str = None):
        guild_id, cat_id = ctx.guild.id, category.id
        
        if name == None:
            name = "➕join to create"
        temp_vc = await category.create_voice_channel(name)

        temp_vc_id, retcode = temp_vc.id, 0

        retcode = jsonfunctions.update_autorole("modules/TemporaryVoiceChannel/json/tempvc.json", guild_id, cat_id, temp_vc_id, retcode)

        if retcode > 0:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="`⚠️`**MISTAKE!**", value=f"**{category.name}** already has a temporary voice channel!")
            conf_embed.set_footer(text=f"Action taken by {ctx.user}.")
        
            await ctx.response.send_message(embed=conf_embed)
            await temp_vc.delete(reason="Already a temp vc in this category")
            return

        conf_embed = discord.Embed(color=discord.Color.red())
        conf_embed.add_field(name="`✅`**Success!**", value=f"Created temporary voice channel **{name}** in {category.name}.")
        conf_embed.set_footer(text=f"Action taken by {ctx.user}.")
        
        await ctx.response.send_message(embed=conf_embed)


    ####################################################################################################################################
    ################################################### Remove Command #################################################################
    ####################################################################################################################################


    @app_commands.command(name="delete_temporary_voice_channel", description="delete a temporary voice channel")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="select the temporary channel you want to delete")
    async def delete_temporary_voice_channel(self, ctx: discord.Interaction, channel: discord.VoiceChannel):
        guild_id, channel_id, cat_id = str(ctx.guild.id), str(channel.id), str(channel.category.id)
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r+") as f:
            data = json.load(f)

            channel_ids = list(data[guild_id].values())

            if channel_id in channel_ids:
                try:
                    data[guild_id].pop(cat_id)

                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)

                except KeyError:
                    await ctx.response.send_message(f"**{channel.name}** is not a temporary voice channel", ephemeral=True)
                    return
            
            else:
                await ctx.response.send_message(f"**{channel.name}** is not a temporary voice channel", ephemeral=True)
                return

        await channel.delete()     

        conf_embed = discord.Embed(color=discord.Color.red())
        conf_embed.add_field(name="`✅`**Success!**", value=f"The temporary voice channel **{channel.name}** in **{channel.category.name}** has been deleted.")
        conf_embed.set_footer(text=f"Action taken by {ctx.user}.")
        
        await ctx.response.send_message(embed=conf_embed)


    ####################################################################################################################################
    ##################################################### List Command #################################################################
    ####################################################################################################################################

    @app_commands.command(name="list_temporary_voice_channels", description="Lists the temporary voice channels for this guild.")
    async def list_join_role(self, interaction: discord.Interaction):
        with open("modules/TemporaryVoiceChannel/json/tempvc.json", "r") as f:
            data = json.load(f)

            if str(interaction.guild.id) not in data or list(data[str(interaction.guild.id)].keys()) == []:
                conf_embed = discord.Embed(color=discord.Color.red())
                conf_embed.add_field(name="`⚠️`**No Temporary Voice Channels!**", value=f"This server has yet to add a temporary voice channel!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

                await interaction.response.send_message(embed=conf_embed)
                return
            
            field = "**Category: Temporary Channel** \n"

            for category_id, channel_id in data[str(interaction.guild.id)].items():
                category = interaction.guild.get_channel(int(category_id))
                field += f"{category.mention}"
                field += "**:** "
                channel = interaction.guild.get_channel(int(channel_id))
                field += f"{channel.mention}"
                field += "**,** "
                field += "\n"

            conf_embed = discord.Embed(color=discord.Color.blue())
            conf_embed.add_field(name="`🔊`**Temporary Voice Channels:**", value=f"{field}")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

            await interaction.response.send_message(embed=conf_embed)


    ####################################################################################################################################
    ################################################# Error Handeling! #################################################################
    ####################################################################################################################################

    @add_temp_voice_channel.error
    async def add_temp_voice_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to add a temporary voice channel!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @delete_temporary_voice_channel.error
    async def delete_temp_voice_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to delete temporary voice channels!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TemporaryVoice(bot))