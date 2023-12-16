import discord
import json
from utils import filepaths as fp
from utils.views import tempvoicekickbanview as tvk
from utils.selectmenus import tempvcselect as tvs
from utils.embeds import embedbuilder as emb
from enum import Enum
import utils.settings as settings
from utils.modals import tempvoicemodals as tvm

logger=settings.logging.getLogger("discord")

class TempVoiceCustomView(discord.ui.View):
    def __init__(self, interaction, bot):
        self.interaction = interaction
        self.bot = bot
        super().__init__(timeout=None)


    ######################## warning embed builder
    @staticmethod #TODO: Small refactoring via creating an embed builder module!
    def warning_embed(user, uservcstate): #user and users voice state, either not in voice or alone
        if uservcstate == VoiceChannelStatus.NotInOwnVoice:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`⚠️` **Failure!**", value=f"{user.mention}, you must be in your own temporary voice channel!")
            return conf_embed
        else:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`⚠️` **Failure!**", value=f"{user.mention}, you can't kick someone if you are alone in your voice channel!")
            return conf_embed
    

    ####################### open json file
    @staticmethod
    def open_temp_vc_json():
        with open(fp.temp_vc_json, "r") as f:
            data = json.load(f)
        return data
    

    ###################### check if member is in own temporary voice channel
    @staticmethod
    def check_if_member_in_own_temp_vc(data, interaction: discord.Interaction):
        success = VoiceChannelStatus.InOwnVoice #set success to "true"
        guild_id = str(interaction.guild.id) #guild_id
        usr_id = interaction.user.id #user_id
        member = interaction.guild.get_member(usr_id)  #get member from user_id for channel
        try:
            member_vc = str(member.voice.channel.id) #member channel_id
        except AttributeError: #if member not in voice channel at all
            success = VoiceChannelStatus.NotInOwnVoice
            return success

        try: #try if the member voice channel is in the data as a key
            vc = data[guild_id][member_vc]["owner"]
        except KeyError:
            success = VoiceChannelStatus.NotInOwnVoice
            return success
        
        if vc != usr_id:  # set success to InOWnVoice if usr_id matchers owner id of the temp voice the user is in
            success = VoiceChannelStatus.NotInOwnVoice
            return success

        if len(member.voice.channel.members) < 2: #if member is alone in his voice
            success = VoiceChannelStatus.AloneInVoice    
        
        return success
    

    ###############################################################################################################################
    ##################################################### Buttons #################################################################
    ###############################################################################################################################

    ###############################################################################################################################
    ##################### kick button #################################################################################


    @discord.ui.button(label="Kick", style=discord.ButtonStyle.gray, custom_id='temp_vc_button_kick', emoji="🚫")
    async def kick_from_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success != VoiceChannelStatus.InOwnVoice: #if user is either not in own temp voice or not in a vc at all
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        await interaction.response.send_message("Choose a member to kick from your temporary voice channel:", ephemeral=True, view=tvk.KickSelectionView())

        return
    
    ###############################################################################################################################
    ##################### ban button #################################################################################


    @discord.ui.button(label="Ban", style=discord.ButtonStyle.gray, custom_id='temp_vc_button_ban', emoji="⛔")
    async def ban_from_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success == VoiceChannelStatus.NotInOwnVoice: # only if user is not in own temp voice, he can ban even if alone in own voice
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        await interaction.response.send_message("Choose a member to ban from your temporary voice channel:", ephemeral=True, view=tvk.BanSelectionView())

        return
    

    ###############################################################################################################################
    ##################### unban button #################################################################################


    @discord.ui.button(label="Unban", style=discord.ButtonStyle.blurple, custom_id='temp_vc_button_unban', emoji="🔰")
    async def unban_from_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success == VoiceChannelStatus.NotInOwnVoice: # only if user is not in own temp voice, he can unban even if alone in own voice
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        await interaction.response.send_message("Choose a member to unban from your temporary voice channel:", ephemeral=True, view=tvk.UnbanSelectionView())

        return
    

    ###############################################################################################################################
    ##################### lock button #################################################################################


    @discord.ui.button(label="Lock", style=discord.ButtonStyle.gray, custom_id='temp_vc_button_lock', emoji="🔒")
    async def lock_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success == VoiceChannelStatus.NotInOwnVoice: # only if user is not in own temp voice, he can unban even if alone in own voice
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        usr_channel = tvs.get_user_channel_from_interaction(interaction)

        everyone = interaction.guild.default_role

        overwrites = usr_channel.overwrites_for(everyone)

        if overwrites.connect == False:
            conf_embed = emb.warn_embed(f"{interaction.user.mention}, your channel is already locked!")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        overwrites = discord.PermissionOverwrite()
        overwrites.connect = False #disabling connecting to the channel

        try: #try setting the permissions
            await usr_channel.set_permissions(everyone, overwrite=overwrites)
        except Exception as e:
            logger.error(e)
            return 

        conf_embed = emb.success_embed(f"{interaction.user.mention} your channel is now locked")
        await interaction.response.send_message(embed=conf_embed, ephemeral=True)

        return
    

    ###############################################################################################################################
    ##################### unlock button #################################################################################


    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.green, custom_id='temp_vc_button_unlock', emoji="🔓")
    async def unlock_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success == VoiceChannelStatus.NotInOwnVoice: # only if user is not in own temp voice, he can unban even if alone in own voice
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        usr_channel = tvs.get_user_channel_from_interaction(interaction)

        everyone = interaction.guild.default_role

        overwrites = usr_channel.overwrites_for(everyone)

        if overwrites.connect == None:
            conf_embed = emb.warn_embed(f"{interaction.user.mention}, your channel is already unlocked!")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        try: #try setting the permissions
            await usr_channel.set_permissions(everyone, overwrite=None)
        except Exception as e:
            logger.error(e)
            return 

        conf_embed = emb.success_embed(f"{interaction.user.mention} your channel is now unlocked")
        await interaction.response.send_message(embed=conf_embed, ephemeral=True)

        return
    

    ###############################################################################################################################
    ##################### user limit button #################################################################################


    @discord.ui.button(label="Set limit", style=discord.ButtonStyle.gray, custom_id='temp_vc_button_set_limit', emoji="👥")
    async def limit_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success == VoiceChannelStatus.NotInOwnVoice: # only if user is not in own temp voice, he can unban even if alone in own voice
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        await interaction.response.send_modal(tvm.TempVoiceUserLimitModal())

        return
    

    ###############################################################################################################################
    ##################### rename button #################################################################################


    @discord.ui.button(label="Rename", style=discord.ButtonStyle.gray, custom_id='temp_vc_button_rename', emoji="✏")
    async def rename_temp_vc(self, interaction, button:discord.ui.Button):
        data = self.open_temp_vc_json()

        #TODO: create method for success call
        success = self.check_if_member_in_own_temp_vc(data, interaction)
        
        if success == VoiceChannelStatus.NotInOwnVoice: # only if user is not in own temp voice, he can unban even if alone in own voice
            conf_embed = self.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        await interaction.response.send_modal(tvm.TempVoiceRenameModal())

        return
    
    
class VoiceChannelStatus(Enum):
    NotInOwnVoice = "NotInOwnVoice"
    AloneInVoice = "AloneInVoice"
    InOwnVoice = "InOwnVoice"