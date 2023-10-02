import discord
from discord.ext import commands
from discord import app_commands
from utils import settings

logger=settings.logging.getLogger("discord")


class serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Serverinfo.py is ready!")

    @app_commands.command(description="Show info about the server")
    async def serverinfo(self, ctx: discord.Interaction):
        name = str(ctx.guild.name)
        description = str(ctx.guild.description)
        guild = ctx.guild
        id = str(ctx.guild.id)
        memberCount = str(ctx.guild.member_count)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        channels = text_channels + voice_channels
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        embed = discord.Embed(
            title=f"{name} Server Information",
            description=f'**Server description**\n {description}',
            color=discord.Color.blue()
        )
        embed.add_field(name='Owner', value=f'{ctx.guild.owner.mention}\n**ID:**({ctx.guild.owner_id})')
        embed.add_field(name="🆔 Server ID", value=id, inline=True)
        embed.add_field(name="👥 Member", value=memberCount, inline=True)
        embed.add_field(name='🤖 Bots', value=f'{sum(member.bot for member in ctx.guild.members)}')
        embed.add_field(name='👥 User', value=f'{sum(not member.bot for member in ctx.guild.members)}')
        embed.add_field(name="💬 Channel", value=f"{channels}", inline=True)
        embed.add_field(name='📆 Server Creation Date', value=f'<t:{int(ctx.guild.created_at.timestamp())}:R>', inline=False)
        embed.add_field(name='🗂 Categories', value=f"{categories}", inline=True)
        embed.add_field(name='Roles', value=str(role_count), inline=False)
        embed.add_field(name='✅ Verification level', value=str(ctx.guild.verification_level), inline=False)
        embed.add_field(name='✨ Boosts', value=f'{str(ctx.guild.premium_subscription_count)}')
        embed.add_field(name='🥇 Boostlevel', value=f'{ctx.guild.premium_tier}')
        embed.add_field(name="```Status```", value=f"**🟢Online:** {statuses[0]}\n**🟠Idle:** {statuses[1]}"
                                                   f"\n**🔴Do not disturb:** {statuses[2]}\n**⚪Offline:** "
                                                   f"{statuses[3]}", inline=True)
        embed.add_field(name='Emojis', value=str(emoji_count), inline=True)
        embed.add_field(name='Rule Channel',
                        value=ctx.guild.rules_channel.mention if ctx.guild.rules_channel else '~~not set~~')
        embed.add_field(name="Community Update Channel",
                        value=ctx.guild.public_updates_channel if ctx.guild.public_updates_channel else "~~not set~~")
        embed.add_field(name='AFK CHANNEL',
                        value=str(ctx.guild.afk_channel.mention if ctx.guild.afk_channel else '~~not set~~'),
                        inline=True)
        embed.add_field(name='AFK Timeout in sec.', value=str(ctx.guild.afk_timeout), inline=True)
        embed.add_field(name="Threads", value=f"{len(guild.threads) if guild.threads else 0}")
        await ctx.response.send_message(embed=embed, view=serverinfob(ctx))


async def setup(bot):
    await bot.add_cog(serverinfo(bot))


class serverinfob(discord.ui.View):
    def __init__(self, ctx):
        self.ctx = ctx
        super().__init__(timeout=None)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.red)
    async def serverinfo2(self, ctx, button:discord.ui.Button):
        name = str(ctx.guild.name)
        description = str(ctx.guild.description)
        guild = ctx.guild
        id = str(ctx.guild.id)
        memberCount = str(ctx.guild.member_count)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        channels = text_channels + voice_channels
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)
        total_member_count = 0
        # Iterate over the voice channels
        for voice_channel in ctx.guild.voice_channels:
            # Sum the number of members connected in each voice channel
            total_member_count += len(voice_channel.members)
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        embed = discord.Embed(
            title=name + " Server Information",
            description=f'**Server Description**\n {description if description else" "}',
            color=discord.Color.blue()
        )
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        embed.add_field(name='Owner', value=f'{ctx.guild.owner.mention}\n**ID:**({ctx.guild.owner_id})')
        embed.add_field(name="🆔 Server ID", value=id, inline=True)
        embed.add_field(name='Shard ID', value=ctx.guild.shard_id if ctx.guild.shard_id else "~~not set~~")
        embed.add_field(name="👥 Member", value=memberCount, inline=True)
        embed.add_field(name='🤖 Bots', value=f'{sum(member.bot for member in ctx.guild.members)}')
        embed.add_field(name='👥 User', value=f'{sum(not member.bot for member in ctx.guild.members)}')
        embed.add_field(name='😢Inactive User', value=await ctx.guild.estimate_pruned_members(days=7))
        embed.add_field(name="💬 Channel", value=channels, inline=True)
        embed.add_field(name="Forums",value=len(guild.forums) if guild.forums else "0")
        embed.add_field(name="Stage Channel", value=guild.stage_channels if guild.stage_channels else "0")
        embed.add_field(name='📆 Server Creation Date', value=f'<t:{int(ctx.guild.created_at.timestamp())}:R>', inline=False)
        embed.add_field(name='🗂 Categories', value=categories, inline=True)
        embed.add_field(name='Roles', value=str(role_count), inline=False)
        embed.add_field(name='✅ Verification Level', value=str(ctx.guild.verification_level), inline=False)
        embed.add_field(name='✨ Boosts', value=f'{str(ctx.guild.premium_subscription_count)}')
        embed.add_field(name='🥇 Boostlevel', value=f'{ctx.guild.premium_tier}')
        embed.add_field(name="```Status```", value=f"**🟢Online:** {statuses[0]}\n**🟠Idle:** {statuses[1]}"
                                                f"\n**🔴Do not disturb:** {statuses[2]}\n**⚪Offline:** "
                                                f"{statuses[3]}", inline=True)
        embed.add_field(name='Emojis', value=str(emoji_count), inline=True)
        embed.add_field(name='Rule Channel',
                        value=ctx.guild.rules_channel.mention if ctx.guild.rules_channel else '~~not set~~')
        embed.add_field(name="Community Update Channel", value=ctx.guild.public_updates_channel if ctx.guild.public_updates_channel else "~~not set~~")
        embed.add_field(name="System-Kanal",value=guild.system_channel.mention)
        embed.add_field(name='AFK CHANNEL',
                        value=str(ctx.guild.afk_channel.mention if ctx.guild.afk_channel else '~~not set~~'),
                        inline=True)
        embed.add_field(name="User in Voice",value=f'**Active Voice Channels**\n{total_member_count} currently in Voice Channels.')    
        embed.add_field(name='AFK Timeout in sec.', value=str(ctx.guild.afk_timeout), inline=True)
        embed.add_field(name='Bitrate', value=(ctx.guild.bitrate_limit if ctx.guild.bitrate_limit else 'keines'),
                        inline=True)
        embed.add_field(name="Vanity URL", value=ctx.guild.vanity_url_code if ctx.guild.vanity_url_code else "~~not set~~")
        embed.add_field(name="Threads",value=guild.threads if guild.threads else 0)
        if guild.features:
            embed.add_field(name="Server features",value="✅"+"\n✅".join(guild.features) or "Nothing")
        embed.set_footer(text=f'Stats requested by {ctx.user.name} • {ctx.user.id}')
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Server Profile", style=discord.ButtonStyle.green)
    async def icon(self, ctx, button:discord.ui.Button):
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
    async def serverrollen(self, ctx, button:discord.ui.Button):
        embed = discord.Embed(title=f"{ctx.guild}`s Server Roles",
                                      description=("".join([str(r.mention) for r in ctx.guild.roles])))
        color=discord.Color.blue()
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Serverbanner", style=discord.ButtonStyle.green)
    async def serverbanner(self, ctx, button:discord.ui.Button):
        if ctx.guild.banner is None:
            embed = discord.Embed(title=f"{ctx.guild}`s Banner", description="No Banner set for server")
            await ctx.response.edit_message(embed=embed)
        else:
            embed = discord.Embed(title=f"{ctx.guild}`s Banner")
            embed.set_image(url=ctx.guild.banner)
            await ctx.response.edit_message(embed=embed)