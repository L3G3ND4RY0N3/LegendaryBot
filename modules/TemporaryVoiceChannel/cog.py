import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import settings, jsonfunctions
import utils.views.tempvoicecustomizationview as tvv
import json

logger=settings.logging.getLogger("discord")

class TemporaryVoice(commands.Cog, name="TemporaryVoice"):
    temp_vc_file_path = "modules/TemporaryVoiceChannel/json/tempchannels.json"
    temp_creation_vc_file_path = "modules/TemporaryVoiceChannel/json/tempcreationvc.json"
    def __init__(self, bot):
        self.bot = bot
        self.temporary_voice_channels = [] #integer list of all temporary voice channels
        self.check_temp_creation_vc.start()
        self.check_temp_vc.start()
    

    def cog_unload(self):
        self.check_temp_creation_vc.cancel()


    def cog_unload(self):
        self.check_temp_vc.cancel()


    #### static methods ######

    @staticmethod
    def remove_deleted_temp_vc_from_json(temp_vc_id):
        with open(TemporaryVoice.temp_vc_file_path, "r+") as f:
            data = json.load(f)
            data = jsonfunctions.remove_nested_keys(data, temp_vc_id)
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        return


    ####################################################################################################################################
    ######################################################### Listener #################################################################
    ####################################################################################################################################

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("TemporaryVoice.py is ready!")
        self.bot.add_view(tvv.TempVoiceCustomView(None, self.bot))

##########################################################################################################################################################################################
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        with open(TemporaryVoice.temp_creation_vc_file_path, "r") as f:
            data = json.load(f)

        guild_id = str(member.guild.id) #get guild id from member

        if guild_id not in data: #if guild not in json of creation channels, exit 
            return

        if after.channel: #if member joined a channel
            vc_id = str(after.channel.id) #get channel id

            temp_vc_list = list(data[guild_id].values()) #list of all creation channel_ids

            temp_vc_channel_name = f"{member.name}'s voice" #temp vc name

            if vc_id in temp_vc_list:
                temp_channel = await after.channel.clone(name=temp_vc_channel_name) #clone creation channel
                await member.move_to(temp_channel) #move member
                self.temporary_voice_channels.append(temp_channel.id) #add temp channel to temp channel list

                #add temp_vc to json file with {server_id: {vc_id:{"owner": owner_id, creation_channel: creation_vc_id}}}
                with open(self.temp_vc_file_path, "r+") as f:
                    data = json.load(f)

                    if guild_id not in data:
                        data[guild_id] = {temp_channel.id: {"owner": member.id, "creation_channel": vc_id}}

                    data[guild_id].update({temp_channel.id: {"owner": member.id, "creation_channel": vc_id}})

                    f.seek(0)

                    json.dump(data, f, indent=4)

        
        if before.channel: #if member left a channel
            if before.channel.id in self.temporary_voice_channels: #if left channel was a temp channel
                if len(before.channel.members) == 0: #if no member left in channel after member left
                    await before.channel.delete() #delete empty temp channel
                    temp_vc_id = str(before.channel.id)
                    with open(self.temp_vc_file_path, "r+") as f:
                        data = json.load(f)

                        data[guild_id].pop(temp_vc_id)                       

                        f.seek(0)
                        f.truncate()

                        json.dump(data, f, indent=4)

##########################################################################################################################################################################################
    # delete the channel from the json, when it gets deleted not using the command
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if type(channel) == discord.TextChannel: #if deleted channel was a text channel exit
            return
        
        guild_id, channel_id, cat_id = str(channel.guild.id), str(channel.id), str(channel.category.id)

        with open(TemporaryVoice.temp_creation_vc_file_path, "r+") as f:
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

##########################################################################################################################################################################################
    # Temp Voice Channels für Multiple Server from Json File
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        with open(TemporaryVoice.temp_creation_vc_file_path, "r") as f:
            data = json.load(f)
        
        data[str(guild.id)] = {}
                    
        with open(TemporaryVoice.temp_creation_vc_file_path, "w") as f:
            json.dump(data, f, indent=4)
##########################################################################################################################################################################################
    # Deletes the temporary voice channels for a server if the bot gets kicked or banned from the server (guild)
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        with open(TemporaryVoice.temp_creation_vc_file_path, "r") as f:
            data = json.load(f)
        
        data.pop(str(guild.id))

        with open(TemporaryVoice.temp_creation_vc_file_path, "w") as f:
            json.dump(data, f, indent=4)


    ####################################################################################################################################
    ######################################################### Tasks ####################################################################
    ####################################################################################################################################

    #Checks if the creation channels have been deleted after bot restart. If so, deletes the category and vc from the json file

    @tasks.loop(minutes=1, count=1)
    async def check_temp_creation_vc(self):
        with open(TemporaryVoice.temp_creation_vc_file_path, "r") as f:
            data = json.load(f)
        guilds = self.bot.guilds
        guild_count = len(guilds)
        vc_channels_ids = []
        count_deleted = 0
        for guild in guilds:
            guild_id = str(guild.id)
            if guild_id not in data:
                    continue
            else:
                for voice_channel in guild.voice_channels:
                    vc_channels_ids.append(voice_channel.id)

        temp_creation_channel_ids = []

        #Iterate over each key in data (server ids)
        for key in data:
            cat_dict = data[key] #get the dictionary of the category_ids with vc_ids as values
            temp_creation_channel_ids += list(cat_dict.values()) #add all vc_ids to the list

        for temp_c_vc_id in temp_creation_channel_ids: #check for every id in json list
            if int(temp_c_vc_id) not in vc_channels_ids: #if id from json file is no longer present in the list of all vc_channel ids
                with open(TemporaryVoice.temp_creation_vc_file_path, "r+") as f:
                    data = json.load(f)
                    data = jsonfunctions.remove_key_with_value(data, temp_c_vc_id) #remove cat_id: vc_channel_id in guild dict
                    f.seek(0)
                    f.truncate()
                    count_deleted += 1
                    json.dump(data, f, indent=4)

        vc_channels_count = len(vc_channels_ids)
        logger.info(f"Checked {vc_channels_count} temporary voice creation channel{'s' if vc_channels_count!=1 else ''} across {guild_count} server{'s' if guild_count!=1 else ''} and registered {count_deleted} deleted temporary voice creation channels!") 


    @check_temp_creation_vc.before_loop
    async def before_check_temp_creation_vc_task(self):
        logger.info("Check temp_creation_vc loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()


    @check_temp_creation_vc.after_loop
    async def after_check_temp_creation_vc_task(self):
        logger.info(f"Finished check temp_creation_vc loop!")
        logger.info("Ending check temporary voice channel creation loop!")


    ##########################################################################################################################################################################################
    #Checks if temporary voice channels still exists on bot reboot and if they got deleted or empty deletes them from the server and json file, else adds them to self.temporary_voice_channels
    ##########################################################################################################################################################################################

    @tasks.loop(minutes=1, count=1)
    async def check_temp_vc(self):
        with open(self.temp_vc_file_path, "r") as f:
            data = json.load(f)
        guilds = self.bot.guilds
        guild_count = len(guilds)
        vc_channels_ids = []
        count_deleted = 0
        for guild in guilds:
            guild_id = str(guild.id)
            if guild_id not in data:
                    continue
            else:
                for voice_channel in guild.voice_channels:
                    vc_channels_ids.append(voice_channel.id)

        temp_channel_ids = []

        #Iterate over each key in data (server ids)
        for key in data:
            temp_channel_ids +=  list(data[key].keys()) #TODO: Add tuple with guild_id for later use!

        #TODO: make function from json command! no code duplicates!

        for temp_vc_id in temp_channel_ids: #check for every id in json list
            if int(temp_vc_id) not in vc_channels_ids: #if id from json file is no longer present in the list of all vc_channel ids
                self.remove_deleted_temp_vc_from_json(temp_vc_id)
                count_deleted += 1
                    

            elif int(temp_vc_id) in vc_channels_ids: #if channel is still existent
                vc = self.bot.get_channel(int(temp_vc_id))
                if len(vc.members) == 0: #if empty delete from server and json file
                    await vc.delete()
                    self.remove_deleted_temp_vc_from_json(temp_vc_id)
                    count_deleted += 1
                        

                else:
                    self.temporary_voice_channels.append(int(temp_vc_id))


        vc_channels_count = len(vc_channels_ids)
        logger.info(f"Checked {vc_channels_count} temporary voice channel{'s' if vc_channels_count!=1 else ''} across {guild_count} server{'s' if guild_count!=1 else ''} and registered {count_deleted} deleted temporary voice channels!") 


    @check_temp_vc.before_loop
    async def before_check_temp_vc_task(self):
        logger.info("Check temp_vc loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()


    @check_temp_vc.after_loop
    async def after_check_temp_vc_task(self):
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
        
        if name is None:
            name = "➕join to create"
        #TODO: add try catch!
        try:
            temp_vc = await category.create_voice_channel(name)
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌`**ERROR!**", value=f"**I am missing the permissions to create voice channels in {category.mention}!**")
            conf_embed.set_footer(text=f"Action taken by {ctx.user}.")
        
            await ctx.response.send_message(embed=conf_embed)
            return

        temp_vc_id, retcode = temp_vc.id, 0

        retcode = jsonfunctions.update_autorole(TemporaryVoice.temp_creation_vc_file_path, guild_id, cat_id, temp_vc_id, retcode)

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
        with open(TemporaryVoice.temp_creation_vc_file_path, "r+") as f:
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

    @app_commands.command(name="list_temporary_voice_channels", description="Lists the temporary voice creation channels for this guild.")
    async def list_temporary_voice_channels(self, interaction: discord.Interaction):
        with open(TemporaryVoice.temp_creation_vc_file_path, "r") as f:
            data = json.load(f)

        if str(interaction.guild.id) not in data or list(data[str(interaction.guild.id)].keys()) == []:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`⚠️`**No Temporary Voice Creation Channels!**", value=f"This server has yet to add a temporary voice creation channel!")
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
    ################################################ Configuration Command #############################################################
    ####################################################################################################################################

    @app_commands.command(name="create_temp_vc_customization", description="Create a reactable message, where users can customize their temporary voice channels")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_temp_vc_customization(self, interaction: discord.Interaction):
        with open(TemporaryVoice.temp_creation_vc_file_path, "r") as f:
            data = json.load(f)

        if str(interaction.guild.id) not in data or list(data[str(interaction.guild.id)].keys()) == []: #TODO: create embed builder!
                conf_embed = discord.Embed(color=discord.Color.red())
                conf_embed.add_field(name="`⚠️`**No Temporary Voice Creation Channels!**", value=f"This server has yet to add a temporary voice creation channel!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

                await interaction.response.send_message(embed=conf_embed)
                return
        
        conf_embed= discord.Embed(color=discord.Color.blue())
        conf_embed.add_field(name="`🔊`**Manage Temporary Voice Channels**", value=f"Configure your own temporary voice channel with the buttons below.")
        await interaction.response.send_message(embed=conf_embed, view=tvv.TempVoiceCustomView(interaction, self.bot))

        return


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


    @create_temp_vc_customization.error
    async def create_temp_vc_customization_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌` **Failure!**", value=f"{interaction.user}, you do not have the permissions to create a customization menu!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TemporaryVoice(bot))