import discord
from utils.embeds import success_embed, reaction_role_embed
import utils.settings as settings
from utils.selectmenus.ReactionRolesSelects import EmojiSelect, RoleSelect
from utils.structs.ReactionRoles import ReactionRolesData
from utils.dbhelpers.reaction_roles_db_helpers import set_reaction_role

logger=settings.logging.getLogger("discord")

class ReactionRoleSetupSetupView(discord.ui.View):
    def __init__(self, bot: discord.Client, guild_id: int, roles: list[discord.Role], channel: discord.TextChannel):
        self.bot = bot
        self.guild_id = guild_id
        self.roles = roles
        self.temp_emoji: str = None
        self.temp_role: int = None
        self.reaction_role_embed_data: list[ReactionRolesData] = []
        self.channel: discord.TextChannel = channel
        super().__init__(timeout=180)
        self.set_reaction_roles.disabled = self.disable_save_button()

    
    def disable_add_button(self) -> bool:
        if len(self.reaction_role_embed_data) >= 20:
            return True
        if len(self.children) > 3:
            return True
        return False
    
    def disable_save_button(self) -> bool:
        if len(self.reaction_role_embed_data) == 0:
            return True
        return False


    # Set Roles button
    @discord.ui.button(label="Set Roles", style=discord.ButtonStyle.green, custom_id='Set_Roles_Reaction_Roles_Setup', emoji="✅")
    async def set_reaction_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = success_embed("Reaction roles have been set up successfully!")
        await interaction.response.edit_message(embed=embed, view=None)
        message = await self.channel.send("Reaction roles have been set up!")
        for data in self.reaction_role_embed_data:
            if data.emoji and data.role_id:
                await message.add_reaction(data.emoji)
                set_reaction_role(guild=interaction.guild, message_id=message.id, role_id=data.role_id, emoji=data.emoji)
        return


    # Quit menu button
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red, custom_id='Quit_Reaction_Roles_Setup', emoji="❌")
    async def quit_reaction_roles_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = success_embed("Aborted setting reaction roles!")
        await interaction.response.edit_message(embed=embed, view=None)
        return
    

    # Add emoji-role pair button
    @discord.ui.button(label="Add Emoji-Role Pair", style=discord.ButtonStyle.blurple, custom_id='Add_Emoji_Role_Pair_Reaction_Roles_Setup', emoji="➕")
    async def add_emoji_role_pair(self, interaction: discord.Interaction, button: discord.ui.Button):
        #self.clear_items()
        self.add_item(EmojiSelect())
        self.add_item(RoleSelect(self.roles))
        if self.disable_add_button():
            button.disabled = True
        embed = reaction_role_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self)
    

    # Disable all buttons when the view times out
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True


    async def check_if_pair_is_ready(self, interaction: discord.Interaction) -> bool:
        if self.temp_role and self.temp_emoji:
            self.reaction_role_embed_data.append(ReactionRolesData(emoji=self.temp_emoji, role_id=self.temp_role))
            embed = reaction_role_embed(interaction.guild, self.reaction_role_embed_data)
            self.temp_emoji = None
            self.temp_role = None
            self.set_reaction_roles.disabled = self.disable_save_button()
            await interaction.response.edit_message(embed=embed, view=self)
            return True
        return False