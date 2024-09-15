import discord
from utils.selectmenus import guildchannelselect as gcs
import utils.settings as settings

logger=settings.logging.getLogger("discord")


class GuildSetupSelectView(discord.ui.View):
    def __init__(self, channel: str, current_page: int, settings_interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.add_item(gcs.GuildSetupChannelSelect(channel, current_page, settings_interaction))