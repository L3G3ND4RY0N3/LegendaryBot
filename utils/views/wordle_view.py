from constants import enums as en
import discord
from utils.embeds import embedbuilder as emb
import utils.settings as settings
from utils.structs.WordleData import WordleData



logger=settings.logging.getLogger("discord")


class WordleView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, bot: discord.Client, wordle_data: WordleData):
        self.wordle_data = wordle_data
        self.user: discord.Member = interaction.user
        super().__init__(timeout=None)


    @discord.ui.button(label="Quit Game", style=discord.ButtonStyle.gray, custom_id='wordle_quit_game', emoji="❌")
    async def wordle_quit_game(self, interaction: discord.Interaction, button:discord.ui.Button):
        if not self.validate_user(interaction.user):
            embed = emb.warn_embed(f"{interaction.user.mention} you are not allowed to press this!")
            await interaction.response.send_message(embed=embed)
            return
        
        # delete game by poping the user_id
        thread: discord.Thread = self.wordle_data.games[self.user.id].thread
        self.wordle_data.update_games_dictionary(self.user.id)

        button.disabled = True
        await interaction.response.edit_message(embed=emb.success_embed(f"Successfully aborted game!"), view=self)
        await thread.delete(reason="Game aborted")
        return
    
    # unecessary as message is ephemeral but here just in case
    def validate_user(self, user: discord.Member) -> bool:
        if user != self.user:
            return False
        return True