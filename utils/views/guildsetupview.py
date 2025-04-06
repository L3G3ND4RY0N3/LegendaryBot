import discord
from utils.dbhelpers.guild_config_db_helpers import get_config_channel_id, get_guild_config, update_channels_guild_config
from utils.embeds import embedbuilder as emb
from utils.embeds.guild_settings_embed import createSettingEmbed
import utils.settings as settings
from utils.views import guildsetupselectview as gssv
from constants import enums as en

logger=settings.logging.getLogger("discord")

class GuildSetupView(discord.ui.View):
    def __init__(self, bot: discord.Client, currentPage: int, channel: str, guild_id: int):
        self.bot = bot
        self.currentPage = currentPage
        self.channel_name = channel
        self.guild_id = guild_id
        super().__init__(timeout=180)
        self.guild_setup_activate.label = self._set_activate_button_label()
        self.guild_setup_deactivate.disabled = self._set_deactivate_button_state()
        self.guild_setup_activate.disabled = self._set_activate_button_state()

    
    def _set_activate_button_label(self) -> str:
        channel_id = get_config_channel_id(get_guild_config(self.guild_id), self.channel_name)
        if channel_id and self.channel_name != en.GuildChannelTypes.ACTIVITY.value:
            return "Update"
        return "Activate"
    
    def _set_deactivate_button_state(self) -> bool:
        channel_id = get_config_channel_id(get_guild_config(self.guild_id), self.channel_name)
        if channel_id:
            return False
        return True
    
    def _set_activate_button_state(self) -> bool:
        channel_id = get_config_channel_id(get_guild_config(self.guild_id), self.channel_name)
        if channel_id and self.channel_name == en.GuildChannelTypes.ACTIVITY.value:
            return True
        return False


    ######################## Buttons 
    
    # Previous Page
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, custom_id='Activate_Guild_Setup_Back', emoji="⬅")
    async def guild_setup_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage -= 1
        embed = createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        self.channel_name = embed.fields[0].name.split(" ")[0].lower()

        await interaction.response.edit_message(embed=embed, view=GuildSetupView(self.bot, self.currentPage, self.channel_name, interaction.guild.id))

        return


    # Next page
    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, custom_id='Activate_Guild_Setup_Forward', emoji="➡")
    async def guild_setup_forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        embed = createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        self.channel_name = embed.fields[0].name.split(" ")[0].lower()

        await interaction.response.edit_message(embed=embed, view=GuildSetupView(self.bot, self.currentPage, self.channel_name, interaction.guild.id))

        return
    

    # Quit menu button
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.grey, custom_id='Activate_Guild_Setup_Quit', emoji="❌")
    async def guild_setup_quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Add logic to display message if no changes were made
        embed = emb.success_embed("Successfully updated guild config!")
        await interaction.response.edit_message(embed=embed, view=None)

        return
    

    ############# deaktivieren der jeweiligen Funktionalität 
    @discord.ui.button(label="Deactivate", style=discord.ButtonStyle.red, custom_id='Deactivate_Guild_Setup', emoji="🛑", row=1)
    async def guild_setup_deactivate(self, interaction: discord.Interaction, button: discord.ui.Button):
        returncode = 0
        # check the status of the given channel, if inactive, deactivate the button
        try:
            update_channels_guild_config(interaction.guild, self.channel_name)
        except Exception as e:
            logger.exception(f"{e}")
            returncode = -1
        if returncode == -1:
            embed = emb.warn_embed(f"There was an error deactivating the {self.channel_name} feature.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = emb.success_embed(f"Successfully deactivated the {self.channel_name} module for this guild!")
        settings_embed = createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        await interaction.response.edit_message(embed=settings_embed, view=GuildSetupView(self.bot, self.currentPage, self.channel_name, interaction.guild.id))
        await interaction.followup.send(embed=embed, ephemeral=True)

        return

    
    ############## aktivieren der jeweiligen Funktionalität, 
    @discord.ui.button(label="Activate", style=discord.ButtonStyle.green, custom_id='Activate_Guild_Setup', emoji="✅", row=1)
    async def guild_setup_activate(self, interaction: discord.Interaction, button: discord.ui.Button):
        retcode = 0
        # If activating or updating the log/error/welcome/bost channel show a select menu
        if self.channel_name.lower() != en.GuildChannelTypes.ACTIVITY.value:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Choose a channel for the {self.channel_name} module: ", view=gssv.GuildSetupSelectView(self.channel_name, self.currentPage, interaction), ephemeral=True)
            return
        else:
            try:
                update_channels_guild_config(interaction.guild, self.channel_name, activity_status=True)
            except Exception as e:
                logger.exception(f"{e}")
                retcode = -1
            if retcode < 0:
                embed = emb.warn_embed(f"There was an error activating the {self.channel_name} feature.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = emb.success_embed(f"Successfully activated the {self.channel_name} module for this guild!")
            settings_embed = createSettingEmbed(interaction.guild, pageNum=self.currentPage)
            await interaction.response.edit_message(embed=settings_embed, view=GuildSetupView(self.bot, self.currentPage, self.channel_name, interaction.guild.id))
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            return