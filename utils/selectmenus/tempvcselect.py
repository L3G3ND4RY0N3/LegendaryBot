import discord
import utils.settings as settings
from utils.embeds import embedbuilder as emb
from utils.views import tempvoicecustomizationview as tcv

logger=settings.logging.getLogger("discord")


def get_user_channel_from_interaction(interaction: discord.Interaction):
        usr_id = interaction.user.id
        member = interaction.guild.get_member(usr_id)
        channel = member.voice.channel
        return channel 


def get_options(members, case):
    options = []
    for member in members:
        if case == "kick":
            options.append(discord.SelectOption(label=member.name, value=member.id, emoji="🚫"))
        else:
            options.append(discord.SelectOption(label=member.name, value=member.id, emoji="✅"))
    return options


#TODO: check if member has a higher role than kicking member or banning

########################################################################################################################################################
######################################k kick select
########################################################################################################################################################

class KickSelectMenu(discord.ui.Select):
    def __init__(self, members): 
        super().__init__(placeholder="Choose a member to kick from your temporary voice channel:", min_values=1, options=get_options(members, "kick"))


    async def callback(self, interaction):
        #TODO: select.disabled = True # make select diabled after kicking one member
        member_id = self.values[0]
        member = interaction.guild.get_member(int(member_id))
        user_mem = interaction.guild.get_member(interaction.user.id)

        if member.id == user_mem.id:
            await interaction.response.send_message(embed=emb.warn_embed(f"{member.mention}, you are unable to kick yourself!"), ephemeral=True)
            return
        
        data = tcv.TempVoiceCustomView.open_temp_vc_json() #get data
        success = tcv.TempVoiceCustomView.check_if_member_in_own_temp_vc(data, interaction) #see if user is still in won voice when using the kick button

        if success != tcv.VoiceChannelStatus.InOwnVoice: #if not in own voice abort
            conf_embed = tcv.TempVoiceCustomView.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        if member.top_role >= user_mem.top_role:
            await interaction.response.send_message(embed=emb.warn_embed(f"{user_mem.mention}, you are unable to kick this member as they have too much power!"), ephemeral=True)
            return
        
        usr_channel = get_user_channel_from_interaction(interaction) #get the channel object TODO:refactor

        try: #try getting the target voice
            mem_channel = member.voice.channel
        except AttributeError:
            mem_channel = None

        if usr_channel != mem_channel: #if taregt not in same voice as interacting user abort
            await interaction.response.send_message(embed=emb.warn_embed(f"Unable to kick {member.mention}, because they are not in your temporary voice channel!"), ephemeral=True)
            return

        try: #try disconnecting the target, if missing permissions abort
            await member.move_to(None)
        except discord.Forbidden:
            await interaction.response.send_message(embed=emb.warn_embed(f"I am unable to kick {member.mention} from your temporary voice channel!"), ephemeral=True)
            return
        
        await interaction.response.send_message(embed=emb.success_embed(f"You kicked {member.mention} from your temporary voice channel!"), ephemeral=True) #success
        

########################################################################################################################################################
######################################### ban select
########################################################################################################################################################

class BanSelectMenu(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Choose a member to ban from your temporary voice channel:", min_values=1)

    async def callback(self, interaction):
        member = self.values[0]
        user_mem = interaction.guild.get_member(interaction.user.id)

        if member.id == user_mem.id:
            await interaction.response.send_message(embed=emb.warn_embed(f"{member.mention}, you are unable to ban yourself!!"), ephemeral=True)
            return
        
        data = tcv.TempVoiceCustomView.open_temp_vc_json() #get data
        success = tcv.TempVoiceCustomView.check_if_member_in_own_temp_vc(data, interaction) #see if user is still in own voice

        if success == tcv.VoiceChannelStatus.NotInOwnVoice: #if not in own voice abort
            conf_embed = tcv.TempVoiceCustomView.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        if member.top_role >= user_mem.top_role:
            await interaction.response.send_message(embed=emb.warn_embed(f"{user_mem.mention}, you are unable to ban this member as they have too much power!"), ephemeral=True)
            return
        
        usr_channel = get_user_channel_from_interaction(interaction) #get channel object
        #get the existing overwrites and check if the targeted member is already banned
        overwrites = usr_channel.overwrites 

        if member in overwrites:
            await interaction.response.send_message(embed=emb.warn_embed(f"{member.mention} is already banned from your temporary voice channel!"), ephemeral=True)
            return

        try: #try get target channel
            mem_channel = member.voice.channel
        except AttributeError:
            mem_channel = None

        if mem_channel == usr_channel: #if target is in users channel, disconnect target
            try:
                await member.move_to(None)
            except discord.Forbidden:
                await interaction.response.send_message(embed=emb.warn_embed(f"I am unable to ban {member.mention} from your temporary voice channel!"), ephemeral=True)
                return
            
        tvc_overwrite = discord.PermissionOverwrite() #create overwrites, so target cant rejoin
        tvc_overwrite.connect = False
        tvc_overwrite.send_messages = False

        try: #try setting the permissions
            await usr_channel.set_permissions(member, overwrite=tvc_overwrite)
        except Exception as e:
            logger.error(e)
            return 
        
        await interaction.response.send_message(embed=emb.success_embed(f"You banned {member.mention} from your temporary voice channel!"), ephemeral=True)
        self.disabled = True


########################################################################################################################################################
######################################### unban select
########################################################################################################################################################

class UnbanSelectMenu(discord.ui.Select):
    def __init__(self, banned_members):
        super().__init__(placeholder="Choose a member to unban from your temporary voice channel:", min_values=1, options=get_options(banned_members, "unban"))

    async def callback(self, interaction):
        member_id = self.values[0]
        member = interaction.guild.get_member(int(member_id))

        if member.id == interaction.user.id:
            await interaction.response.send_message(embed=emb.warn_embed(f"{member.mention}, you are unable to unban yourself!!"), ephemeral=True)
            return
        
        data = tcv.TempVoiceCustomView.open_temp_vc_json() #get data
        success = tcv.TempVoiceCustomView.check_if_member_in_own_temp_vc(data, interaction) #see if user is still in own voice

        if success == tcv.VoiceChannelStatus.NotInOwnVoice: #if not in own voice abort
            conf_embed = tcv.TempVoiceCustomView.warning_embed(interaction.user, success)
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return
        
        usr_channel = get_user_channel_from_interaction(interaction) #get channel object

        try: #try setting the permissions
            await usr_channel.set_permissions(member, overwrite=None)
        except Exception as e:
            logger.error(e)
            return 
        
        await interaction.response.send_message(embed=emb.success_embed(f"You unbanned {member.mention} from your temporary voice channel!"), ephemeral=True)