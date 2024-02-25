import discord
from utils.selectmenus import guildchannelselect as gcs
import utils.settings as settings

logger=settings.logging.getLogger("discord")


class GuildSetupSelectView(discord.ui.View):
    def __init__(self, channel: str):
        super().__init__(timeout=None)
        self.add_item(gcs.GuildSetupChannelSelect(channel))