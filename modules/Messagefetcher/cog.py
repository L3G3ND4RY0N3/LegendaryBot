import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import json
from utils import settings

logger=settings.logging.getLogger("discord")

class MessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("Messagefetcher.py is ready!")

    @app_commands.command(name="export_messages", description="Export messages from a channel using some filters and return them in a json file.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel = "Select a channel", cutoff_date="Select a date (format: yyyy-mm-dd), older messages won't be exported!", msg_filter="the filter, starting at the beginning of the message", filename="what the exported file should be named", msg_limit="the amount of messages (max 200)")
    async def export_messages(self, interaction: discord.Interaction, msg_filter: str, msg_limit:int, filename:str, channel: discord.TextChannel = None, cutoff_date: str = "1970-01-01"):
        try:
            cutoff_date = datetime.strptime(cutoff_date, '%Y-%m-%d')
        except ValueError:
            await interaction.response.send_message('Invalid date format! Please enter your date like this: "YYYY-MM-DD".')
            return

        if not channel:
            channel = interaction.channel

        messages = []
        
        async for message in channel.history(limit=msg_limit, oldest_first=False):
            if message.created_at.date() > cutoff_date.date():
                if message.content.startswith(f'{msg_filter}'):
                    try:
                        title=message.embeds[0].title
                    except:
                        title = ""
                    messages.append({
                        'Datum': f"{message.created_at.day}.{message.created_at.month}.{message.created_at.year}",
                        'Inhalt': message.content,
                        'Titel': title
                    })

        if not messages:
            await interaction.response.send_message('No messages found for these filter settings!')
        else:
            with open(f'modules/Messagefetcher/json/{filename}.json', 'w') as file:
                json.dump(messages, file, indent=4)

            file = discord.File(f'modules/Messagefetcher/json/{filename}.json', filename=f"{filename}.json")
            await interaction.response.send_message('Messages have been exported!',file=file)


    @export_messages.error
    async def export_messages_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌`**Failure**!", value=f"{interaction.user.name}, you do not have the permissions to export messages! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MessageCog(bot))