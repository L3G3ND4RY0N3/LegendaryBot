from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from .base import Base
import dbmodels


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    guild_dc_id = Column(Integer,  unique=True)
    name = Column(String)

    members: Mapped["Member"] = relationship("Member", back_populates="guild")


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    server_name = Column(String)

    user: Mapped["dbmodels.User"] = relationship("User", back_populates="members")
    guild: Mapped["Guild"] = relationship("Guild", back_populates="members")
    activities: Mapped["dbmodels.Activity"] = relationship("Activity", back_populates="member")