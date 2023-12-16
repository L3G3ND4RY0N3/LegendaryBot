import discord
from utils.selectmenus import tempvcselect as ts
import utils.settings as settings

logger=settings.logging.getLogger("discord")


class KickSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ts.KickSelectMenu())


class BanSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ts.BanSelectMenu())


class UnbanSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ts.UnbanSelectMenu())