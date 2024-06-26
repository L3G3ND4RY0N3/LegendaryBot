from constants import enums as en
import discord
from utils.embeds import embedbuilder as emb
import utils.settings as settings



logger=settings.logging.getLogger("discord")


class WordleView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, bot: discord.Client, data):
        self.interaction = interaction
        self.bot = bot
        self.data = data
        self.user: discord.Member = interaction.user
        super().__init__(timeout=None)


    @discord.ui.button(label="Quit Game", style=discord.ButtonStyle.gray, custom_id='wordle_quit_game', emoji="❌")
    async def wordle_quit_game(self, interaction: discord.Interaction, button:discord.ui.Button):
        if not self.validate_user(interaction.user):
            embed = emb.warn_embed(f"{interaction.user.mention} you aree not allowed to press this!")
            await interaction.response.send_message(embed=embed)
            return
        
        # delete game by deleting thread from data
        thread: discord.Thread = self.data.thread
        self.data.thread = None

        await interaction.response.send_message(embed=emb.success_embed(f"Successfully aborted game"), ephemeral=True)
        await thread.delete(reason="Game aborted")

        return
    
    # unecessary as message is ephemeral but here just in case
    def validate_user(self, user: discord.Member) -> bool:
        if user != self.user:
            return False
        return True