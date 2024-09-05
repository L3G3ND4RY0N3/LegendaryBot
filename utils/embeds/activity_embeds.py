import discord
import utils.settings as settings


logger=settings.logging.getLogger("discord")

# TODO: fix hardcoded dict dependencies!
def activity_stats_embed(stats: dict, member: discord.Member) -> discord.Embed:
    emb = discord.Embed(color=discord.Color.blurple(),
                        title=f"Activity stats for {member.name}"
                        )
    emb.add_field(name="Sent Messages", value=f'Messages sent: {stats.get("message_count", 0)}', inline=False)
    emb.add_field(name="Time in Voice", value=f'Minutes in Voice: {stats.get("minutes_in_voice", 0)}', inline=False)
    emb.add_field(name="XP", value=f'Experience: {stats.get("xp", 0)}', inline=False)
    emb.set_footer(text=f"Requested by {member.global_name}")
    return emb


def guild_leaderboard_embed(table: str, order: str, member: discord.Member) -> discord.Embed:
    emb = discord.Embed(color=discord.Color.blurple(),
                        title=f"Activity Leaderboard for {member.guild.name}",
                        description=f"```\n{table}\n```"
                        )
    emb.set_footer(text=f"Requested by {member.global_name}, leaderboard sorted by {order}")
    return emb