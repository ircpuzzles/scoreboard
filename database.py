from sqlalchemy import create_engine, orm, Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://ircpuzzles:ircpuzzles@localhost/ircpuzzles')
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    account = Column(String)
    confirmed = Column(Boolean)
    password = Column(String)
    confirmation_code = Column(String)

    def __repr__(self):
        return "<User(account='%s', confirmed='%s')>" % (self.account, str(self.confirmed))

class GameInfo(Base):
    """Information about running game, used by the bot and webapp 
    to create the Game() instances.
    """
    __tablename__ = 'game_infos'

    id = Column(Integer, primary_key=True)

    # absolute path to the game.json
    path = Column(String(512))
    running = Column(Boolean)

    def __repr__(self):
        return "<GameInfo(%d, path='%s', running='%s')>" % (self.id, self.path, str(self.running))

class Join(Base):
    __tablename__ = 'joins'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User',foreign_keys='Join.user_id')
    channel = Column(String)
    time = Column(DateTime, default=func.now())


def init_db():
    Base.metadata.create_all(engine)
