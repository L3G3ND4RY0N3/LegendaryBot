import typing
import discord
from discord.ui import Select

if typing.TYPE_CHECKING:
    from utils.views.ReactionRoleSetupView import ReactionRoleSetupSetupView


class EmojiSelect(Select):
    def __init__(self):
        self.view : ReactionRoleSetupSetupView
        super().__init__(
            placeholder="Choose an emoji...",
            #TODO: Dynamically load emojis from the guild and remove duplicates
            options=[
                discord.SelectOption(label="😀", value="😀"),
                discord.SelectOption(label="🔥", value="🔥"),
                discord.SelectOption(label="💎", value="💎"),
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        # Store selection in the parent view
        self.view.temp_emoji = self.values[0]
        if await self.view.check_if_pair_is_ready(interaction):
            return
        await interaction.response.defer()


class RoleSelect(Select):
    def __init__(self, roles: list[discord.Role]):
        self.view : ReactionRoleSetupSetupView
        #TODO: Filter out @everyone role and remove duplicates
        super().__init__(
            placeholder="Choose a role...",
            options=[discord.SelectOption(label=r.name, value=str(r.id)) for r in roles]
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.temp_role = int(self.values[0])
        if await self.view.check_if_pair_is_ready(interaction):
            return
        await interaction.response.defer()