import pytest
from constants.enums import GuildChannelDBColumns, GuildChannelTypes
from dbmodels.guild_models import GuildConfig

# if I change the db columns please alert
def test_guildconfig_error_column():
    assert GuildChannelDBColumns.ERROR.value in GuildConfig.__table__.columns

def test_guildconfig_log_column():
    assert GuildChannelDBColumns.LOG.value in GuildConfig.__table__.columns

def test_guildconfig_welcome_column():
    assert GuildChannelDBColumns.WELCOME.value in GuildConfig.__table__.columns

def test_guildconfig_boost_column():
    assert GuildChannelDBColumns.BOOST.value in GuildConfig.__table__.columns

def test_guildconfig_activity_column():
    assert GuildChannelDBColumns.ACTIVITY.value in GuildConfig.__table__.columns

# for checking if the db column names entail the embed titles
def test_guildconfig_error_name():
    assert GuildChannelTypes.ERROR.value in GuildChannelDBColumns.ERROR.value

def test_guildconfig_log_name():
    assert GuildChannelTypes.LOG.value in GuildChannelDBColumns.LOG.value

def test_guildconfig_welcome_name():
    assert GuildChannelTypes.WELCOME.value in GuildChannelDBColumns.WELCOME.value

def test_guildconfig_boost_name():
    assert GuildChannelTypes.BOOST.value in GuildChannelDBColumns.BOOST.value

def test_guildconfig_activity_name():
    assert GuildChannelTypes.ACTIVITY.value in GuildChannelDBColumns.ACTIVITY.value