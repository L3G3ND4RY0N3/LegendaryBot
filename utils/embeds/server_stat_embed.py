import discord

def create_server_stat_embed(ctx: discord.Interaction)->discord.Embed:
    """Creates an embed for server statistics

    Returns:
        discord.Embed: The server statistics embed
    """
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
    if guild.features:
        embed.add_field(name="Server features",value="✅"+"\n✅".join(guild.features) or "Nothing")
    embed.set_footer(text=f'Stats requested by {ctx.user.name} • {ctx.user.id}')

    return embed