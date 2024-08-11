import discord
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, get_db_session


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    guild_dc_id = Column(Integer,  unique=True)
    name = Column(String)

    members = relationship("Member", back_populates="guild")


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    server_name = Column(String)

    user = relationship("User", back_populates="members")
    guild = relationship("Guild", back_populates="members")
    activities = relationship("Activity", back_populates="member")