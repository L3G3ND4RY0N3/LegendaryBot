import pytest

from utils.guildjsonfunctions import check_guild_channel_status
from constants.enums import GuildChannelTypes as gct, GuildChannelStatus as GCS



@pytest.fixture()
def guild_id1() -> str:
    return "1156877413788164216"


@pytest.fixture()
def guild_id2() -> str:
    return "910526904174510120"


@pytest.fixture()
def fpath() -> str:
    return "tests/json/guildchanneltest.json"


def test_check_status_guild1(guild_id1: str, fpath: str):
    assert check_guild_channel_status(guild_id1, gct.ACTIVITY.value, fpath) == GCS.Active
    assert check_guild_channel_status(guild_id1, gct.ERROR.value, fpath) == GCS.Active
    assert check_guild_channel_status(guild_id1, gct.LOG.value, fpath) == GCS.Inactive
    assert check_guild_channel_status(guild_id1, gct.WELCOME.value, fpath) == GCS.Inactive
    assert check_guild_channel_status(guild_id1, gct.BOOST.value, fpath) == GCS.Inactive


def test_check_status_guild2(guild_id2: str, fpath: str):
    assert check_guild_channel_status(guild_id2, gct.ACTIVITY.value, fpath) == GCS.Inactive
    assert check_guild_channel_status(guild_id2, gct.ERROR.value, fpath) == GCS.Active
    assert check_guild_channel_status(guild_id2, gct.LOG.value, fpath) == GCS.Inactive
    assert check_guild_channel_status(guild_id2, gct.WELCOME.value, fpath) == GCS.Active
    assert check_guild_channel_status(guild_id2, gct.BOOST.value, fpath) == GCS.Active


def test_check_status_guild_not_found(fpath: str):
    assert check_guild_channel_status("12345", gct.ACTIVITY.value, fpath) == GCS.GuildNotSet
    assert check_guild_channel_status("12345", gct.ERROR.value, fpath) == GCS.GuildNotSet