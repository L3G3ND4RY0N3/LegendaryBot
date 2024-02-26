import pytest

from utils.guildjsonfunctions import check_guild_channel_status
from constants.enums import GuildChannelTypes as gct



@pytest.fixture()
def guild_id1() -> str:
    return "1156877413788164216"


@pytest.fixture()
def guild_id2() -> str:
    return "910526904174510120"


@pytest.fixture()
def fpath() -> str:
    return "tests/json/guildchanneltest.json"


def test_check_status_guild1(guild_id1, fpath):
    assert check_guild_channel_status(guild_id1, gct.ACTIVITY.value, fpath) == 1
    assert check_guild_channel_status(guild_id1, gct.ERROR.value, fpath) == 1
    assert check_guild_channel_status(guild_id1, gct.LOG.value, fpath) == 0
    assert check_guild_channel_status(guild_id1, gct.WELCOME.value, fpath) == 0
    assert check_guild_channel_status(guild_id1, gct.BOOST.value, fpath) == 0


def test_check_status_guild2(guild_id2, fpath):
    assert check_guild_channel_status(guild_id2, gct.ACTIVITY.value, fpath) == 0
    assert check_guild_channel_status(guild_id2, gct.ERROR.value, fpath) == 1
    assert check_guild_channel_status(guild_id2, gct.LOG.value, fpath) == 0
    assert check_guild_channel_status(guild_id2, gct.WELCOME.value, fpath) == 1
    assert check_guild_channel_status(guild_id2, gct.BOOST.value, fpath) == 1


def test_check_status_guild_not_found(fpath):
    assert check_guild_channel_status("12345", gct.ACTIVITY.value, fpath) == -1
    assert check_guild_channel_status("12345", gct.ERROR.value, fpath) == -1