import discord
from discord.ext import commands
from discord import app_commands
from utils import settings
from utils.embeds.server_stat_embed import create_server_stat_embed

logger=settings.logging.getLogger("discord")


class serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")

    @app_commands.command(description="Show info about the server")
    async def serverinfo(self, ctx: discord.Interaction):
        embed = create_server_stat_embed(ctx)
        await ctx.response.send_message(embed=embed, view=serverinfob(ctx))


async def setup(bot):
    await bot.add_cog(serverinfo(bot))


class serverinfob(discord.ui.View):
    def __init__(self, ctx):
        self.ctx = ctx
        super().__init__(timeout=None)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.red)
    async def serverinfo2(self, ctx: discord.Interaction, button: discord.ui.Button):
        """Home button to go back to main embed"""
        embed = create_server_stat_embed(ctx)
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Server Profile", style=discord.ButtonStyle.green)
    async def icon(self, ctx: discord.Interaction, button:discord.ui.Button):
        embed = discord.Embed(title=f"Server Icon of {ctx.guild}")
        embed.set_image(url=ctx.guild.icon)
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Server emojis", style=discord.ButtonStyle.blurple)
    async def serveremoji(self, ctx, button:discord.ui.Button):
        embed = discord.Embed()
        embed = discord.Embed(title=f"{ctx.guild}`s Serveremojis",
        description=(",".join([str(emojis) for emojis in ctx.guild.emojis])),
        color=discord.Color.blue())
        try:
            await ctx.response.edit_message(embed=embed)
        except Exception as e:
            logger.warning(f"{e}")

    @discord.ui.button(label="Server Roles", style=discord.ButtonStyle.blurple)
    async def serverrollen(self, ctx: discord.Interaction, button:discord.ui.Button):
        embed = discord.Embed(title=f"{ctx.guild}`s Server Roles",
                            description=("".join([str(r.mention) for r in ctx.guild.roles])), color=discord.Color.blue())
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Serverbanner", style=discord.ButtonStyle.green)
    async def serverbanner(self, ctx: discord.Interaction, button:discord.ui.Button):
        if ctx.guild.banner is None:
            embed = discord.Embed(title=f"{ctx.guild}`s Banner", description="No Banner set for server")
            await ctx.response.edit_message(embed=embed)
        else:
            embed = discord.Embed(title=f"{ctx.guild}`s Banner")
            embed.set_image(url=ctx.guild.banner)
            await ctx.response.edit_message(embed=embed)