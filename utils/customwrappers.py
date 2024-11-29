from dotenv import load_dotenv
import os
import typing as T
import discord
import functools


_ = load_dotenv()

OWNER = int(os.getenv('OWNER', 0))

#region GENERAL USE
class CountFuncCalls:
    def __init__(self, max_count: int = 1):
        self.max_count: int = max_count
        self.call_count: dict[str, int] = {}

    def __call__(self, func: T.Any):
        def wrapper(*args: T.Any, **kwargs: T.Any):
            if func.__name__ not in self.call_count:
                self.call_count[func.__name__] = 0

            self.call_count[func.__name__] += 1

            if self.call_count[func.__name__] > self.max_count:
                print(f"Function '{func.__name__}' called more than {self.max_count} times!")
                return
            return func(*args, **kwargs)
        
        wrapper.get_call_count = lambda: self.call_count.get(func.__name__, 0)
        return wrapper


def repeat_func(num: int):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat
#endregion

#region DISCORD DECORATORS

def is_owner():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == OWNER
    return discord.app_commands.check(predicate)


async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CheckFailure):
        embed = discord.Embed(title="Access Denied", description="You are not allowed to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        if interaction.user.id == OWNER:
            await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred, please try again later!", ephemeral=True)

#endregion