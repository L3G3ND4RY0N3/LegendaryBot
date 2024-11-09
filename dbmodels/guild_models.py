from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from .base import Base
import dbmodels


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    guild_dc_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)

    members: Mapped["Member"] = relationship("Member", back_populates="guild")
    guild_config: Mapped["GuildConfig"] = relationship("GuildConfig", back_populates="guild")
    autodelete_channels: Mapped["AutoDeleteChannel"] = relationship("AutoDeleteChannel", back_populates="guild")


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    server_name = Column(String, nullable=False)

    user: Mapped["dbmodels.User"] = relationship("User", back_populates="members")
    guild: Mapped["Guild"] = relationship("Guild", back_populates="members")
    activities: Mapped["dbmodels.Activity"] = relationship("Activity", back_populates="member")
    warnings: Mapped["ModWarning"] = relationship("ModWarning", back_populates="member")


class GuildConfig(Base):
    __tablename__ = 'guildconfigs'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), unique=True)
    error_channel_id = Column(Integer, default=0)
    welcome_channel_id = Column(Integer, default=0)
    boost_channel_id = Column(Integer, default=0)
    log_channel_id = Column(Integer, default=0)
    activity_status = Column(Boolean, default=False)

    guild: Mapped["Guild"] = relationship("Guild", back_populates="guild_config")


    def update_channels(self, error_id: int | None = None,
                        welcome_id: int | None = None,
                        boost_id: int | None = None,
                        log_id: int | None = None) -> None:
        if error_id:
            self._update_error_channel(error_id)
        if welcome_id:
            self._update_weclome_channel(welcome_id)
        if boost_id:
            self._update_boost_channel(boost_id)
        if log_id:
            self._update_log_channel(log_id)


    def update_activity(self, activity: bool) -> None:
        self.activity_status = activity


    def _update_error_channel(self, error_id: int) -> None:
        self.error_channel_id = error_id

    def _update_weclome_channel(self, welcome_id: int) -> None:
        self.welcome_channel_id = welcome_id
    
    def _update_boost_channel(self, boost_id: int) -> None:
        self.boost_channel_id = boost_id

    def _update_log_channel(self, log_id: int) -> None:
        self.log_channel_id = log_id


class ModWarning(Base):
    __tablename__ = 'modwarnings'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    mod_id = Column(Integer, ForeignKey('users.id'))
    warns = Column(Integer, default=0, nullable=False)
    warn_reason = Column(String, default=u'')
    warn_time = Column(DateTime(timezone=True), server_default=func.now())

    member: Mapped["Member"] = relationship("Member", back_populates="warnings")
    user: Mapped["dbmodels.User"] = relationship("User", back_populates="warns_given")


class AutoDeleteChannel(Base):
    __tablename__ = 'autodeletechannels'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    channel_id = Column(Integer, nullable=False)
    max_messages = Column(Integer, default=0)
    delay_in_minutes = Column(Integer, default=0)

    guild: Mapped["Guild"] = relationship("Guild", back_populates="autodelete_channels")