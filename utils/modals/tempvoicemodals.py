from discord import ui
from discord.interactions import Interaction
import utils.settings as settings
from utils.selectmenus import tempvcselect as tvs
from utils.embeds import embedbuilder as emb

logger=settings.logging.getLogger("discord")


class TempVoiceUserLimitModal(ui.Modal, title="Set user limit for your voice channel"):
    usr_limit = ui.TextInput(label="User limit", placeholder="Select a number between 0 - 99, with 0 meaning no limit.")

    async def on_submit(self, interaction: Interaction):
        usr_channel = tvs.get_user_channel_from_interaction(interaction)

        try:
            limit = int(self.usr_limit)
        except ValueError:
            conf_embed = emb.warn_embed(f"{interaction.user.mention}, please enter a valid integer!")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        try: #try edit the limit of the channel
            await usr_channel.edit(user_limit=limit)
        except Exception as e:
            logger.error(e)
            return 

        conf_embed = emb.success_embed(f"{interaction.user.mention} your channel is now limited to {limit} users.") #TODO: print the amount
        await interaction.response.send_message(embed=conf_embed, ephemeral=True)


####################################################################################################################################################
########################## Rename Modal
####################################################################################################################################################


class TempVoiceRenameModal(ui.Modal, title="Set a new name for your channel"):
    name = ui.TextInput(label="Name", placeholder="Set a name")

    async def on_submit(self, interaction: Interaction):
        usr_channel = tvs.get_user_channel_from_interaction(interaction)

        name = self.name

        try: #try edit the limit of the channel
            await usr_channel.edit(name=name)
        except Exception as e:
            logger.error(e)
            return 

        conf_embed = emb.success_embed(f"{interaction.user.mention} your channel has been renamed to {name}.") #TODO: print the amount
        await interaction.response.send_message(embed=conf_embed, ephemeral=True)