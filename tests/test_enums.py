import pytest
from constants.enums import GuildChannelTypes as GCT


def test_error_channel_value():
    assert GCT.ERROR.value == "error"


def test_log_channel_value():
    assert GCT.LOG.value == "log"


def test_boost_channel_value():
    assert GCT.BOOST.value == "boost"


def test_activity_channel_value():
    assert GCT.ACTIVITY.value == "activity"


def test_welcome_channel_value():
    assert GCT.WELCOME.value == "welcome"