import discord
from utils.embeds import embedbuilder as emb
from utils.embeds.guild_settings_embed import createSettingEmbed
import utils.settings as settings
from utils import guildjsonfunctions as GJF
from utils.views import guildsetupselectview as gssv
from constants import enums as en

logger=settings.logging.getLogger("discord")

class GuildSetupView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, bot, currentPage, channel):
        self.interaction = interaction
        self.bot = bot
        self.currentPage = currentPage
        self.channel = channel
        self.guid_id = interaction.guild.id
        super().__init__(timeout=180)


    ######################## Buttons 
    
    # Previous Page
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, custom_id='Activate_Guild_Setup_Back', emoji="⬅")
    async def guild_setup_back(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.currentPage -= 1
        embed = createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        self.channel = embed.fields[0].name.split(" ")[0].lower()

        await interaction.response.edit_message(embed=embed, view=GuildSetupView(interaction, self.bot, self.currentPage, self.channel))

        return


    # Next page
    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, custom_id='Activate_Guild_Setup_Forward', emoji="➡")
    async def guild_setup_forward(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.currentPage += 1
        embed = createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        self.channel = embed.fields[0].name.split(" ")[0].lower()

        await interaction.response.edit_message(embed=embed, view=GuildSetupView(interaction, self.bot, self.currentPage, self.channel))

        return
    

    # Quit menu button
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.grey, custom_id='Activate_Guild_Setup_Quit', emoji="❌")
    async def guild_setup_quit(self, interaction: discord.Interaction, button:discord.ui.Button):
        # TODO: build final embed ^^
        await interaction.response.edit_message(content="Bye!", embed=None, view=None)

        return
    

    ############# deaktivieren der jeweiligen Funktionalität 
    @discord.ui.button(label="Deactivate", style=discord.ButtonStyle.red, custom_id='Deactivate_Guild_Setup', emoji="🛑", row=1)
    async def guild_setup_deactivate(self, interaction: discord.Interaction, button:discord.ui.Button):
        guild_id = str(interaction.guild.id)
        returncode = 0
        # check the status of the given channel, if inactive, deactivate the button
        try:
        # if for some reason anything fails, log the exception and still send an embed
            # check if activity or channels are updated
            if self.channel != en.GuildChannelTypes.ACTIVITY.value:
                returncode = GJF.update_guild_channel(guild_id, 0, self.channel)
            else:
                returncode = GJF.update_activity_tracker(guild_id, 0)
        except Exception as e:
            logger.exception(f"{e}")
            returncode = -1
        # TODO: add error to error channel, if setup
        if returncode < 0:
            embed = emb.warn_embed(f"There was an error deactivating the {self.channel} feature.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = emb.success_embed(f"Successfully deactivated the {self.channel} module for this guild!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        return

    
    ############## aktivieren der jeweiligen Funktionalität, 
    @discord.ui.button(label="Activate/Update", style=discord.ButtonStyle.green, custom_id='Activate_Guild_Setup', emoji="✅", row=1)
    async def guild_setup_activate(self, interaction: discord.Interaction, button:discord.ui.Button):
        retcode = 0
        if self.channel.lower() != en.GuildChannelTypes.ACTIVITY.value:
            await interaction.response.send_message(f"Choose a channel for the {self.channel} module: ", view=gssv.GuildSetupSelectView(self.channel), ephemeral=True)
            return
        else:
            retcode = GJF.update_activity_tracker(str(interaction.guild.id), 1)
            if retcode < 0:
                embed = emb.warn_embed(f"There was an error activating the {self.channel} feature.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = emb.success_embed(f"Successfully activated the {self.channel} module for this guild!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return