import discord
from dataclasses import dataclass
from ..Wordle.wordle import Wordle, GameState


@dataclass
class PlayerData():
    """A dataclass storing the information of an ongoing game of any player
    """
    game: Wordle = None
    thread: discord.Thread = None
    embed: discord.Embed = None
    message: discord.Message = None



class WordleData():                                                                                                                                                                                                                                                  
    """Class that stores information of all games for all players by their id
    """
    def __init__(self):
        self.games: dict[int, PlayerData] = {}

    
    def update_games_dictionary(self, user_id: int, player_data: PlayerData | None = None) -> bool:
        # if new game, set all variables
        if user_id not in self.games:
            self.games[user_id] = player_data
            return True
        
        # if no playerdata, pop user
        if not player_data:
            self.games.pop(user_id)
            return True

        # if game is over remove the user and their game from the dict
        if player_data.game.gamestate != GameState.ONGOING:
            self.games.pop(user_id)
            return True
        
        # if thread, message or embed is gone, abort
        if not player_data.thread or not player_data.embed or not player_data.message:
            self.games.pop(user_id)
            return True
        
        return False
        

    def find_player_id_by(self, thread: discord.Thread | None = None, embed: discord.Embed | None = None, message: discord.Message | None = None) -> int | None:
        for player_id, player_data in self.games.items():
            if player_data.thread == thread:
                return player_id
            
            if player_data.embed == embed:
                return player_id
            
            if player_data.message == message:
                return player_id
            
        # if nothing found return None    
        return None