import discord
import utils.settings as settings
import utils.guildjsonfunctions as gjf
from utils.embeds import embedbuilder as emb

logger=settings.logging.getLogger("discord")


class GuildSetupChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, channel: str): 
        self.channel_name = channel
        super().__init__(placeholder=f"Choose a channel for the {channel} module:", min_values=1, channel_types=[discord.ChannelType.text])


    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        channel_id = channel.id
        guild_id = str(channel.guild.id)
        returncode: int = 0
        try:
            returncode = gjf.update_guild_channel(guild_id, channel_id, self.channel_name)
        except Exception as e:
            logger.error(f"**Error setting the channel for the {self.channel_name} module in {channel.guild.name} with id {guild_id}**")
            logger.exception(f"{e}")

        if returncode < 0:
            embed = emb.warn_embed(f"**There was an error activating the {self.channel_name} feature.**")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = emb.success_embed(f"**Successfully activated the {self.channel_name} module in {channel.mention} for this guild!**")
        await interaction.response.send_message(embed=embed, ephemeral=True)