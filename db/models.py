from datetime import datetime

from db.base import Base, engine, Session
from sqlalchemy import Column, Integer, String, Numeric, Date, func, DateTime, ForeignKey

FREQUENCY_OPTIONS = ('DAILY', 'NEVER')
REACTIONS_OPTIONS = ('LIKE', 'DISLIKE', 'SEEN')


# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class ModelError(Exception):
    pass


class User(Base):
    __tablename__ = 'fb_bot_users'
    user_id = Column('id', String(32), primary_key=True)
    frequency = Column('frequency', String(32))
    creation_date = Column('creation_date', DateTime)

    def __init__(self, user_id, frequency, **kwargs):
        self.user_id = user_id
        if frequency not in FREQUENCY_OPTIONS:
            raise ModelError(f'frequency must be one of {FREQUENCY_OPTIONS}')
        self.frequency = frequency
        self.creation_date = kwargs.get('creation_date', datetime.now())

    def __str__(self):
        return f'user[id={self.user_id}, frequency={self.frequency}, creation_date={self.creation_date}]'

    def __repr__(self):
        return {
            'user_id': self.user_id,
            'frequency': self.frequency,
            'creation_date': self.creation_date.isoformat(),
        }


class Quote(Base):
    __tablename__ = 'fb_bot_quotes'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    creation_date = Column('creation_date', DateTime)
    text = Column('text', String(350))
    author = Column('author', String(30))
    seen_count = Column('seen_count', Integer)
    like_count = Column('like_count', Integer)
    dislike_count = Column('dislike_count', Integer)

    def __init__(self, text, author, **kwargs):
        self.creation_date = kwargs.get('creation_date', datetime.now())
        self.text = text
        self.author = author
        self.seen_count = 0
        self.like_count = 0
        self.dislike_count = 0

    def __str__(self):
        return f'Quote[id={self.id}, creation_date={self.creation_date}, ' \
               f'text={self.text}, author={self.author}]'

    def as_text(self):
        return f'"{self.text}" by *{self.author}*'


class Reaction(Base):
    __tablename__ = 'fb_bot_user_quote'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user = Column('user_id', String, ForeignKey('fb_bot_users.id'))
    quote = Column('quote_id', Integer, ForeignKey('fb_bot_quotes.id'))
    seen_date = Column('seen_date', Date)
    reaction = Column('reaction', String(10))

    def __init__(self, user_id, quote_id, reaction, **kwargs):
        self.user = user_id
        self.quote = quote_id
        if reaction not in REACTIONS_OPTIONS:
            raise ModelError(f'reaction must be one of {REACTIONS_OPTIONS}')
        self.reaction = reaction
        self.seen_date = kwargs.get('creation_date', datetime.now().date())

    def __str__(self):
        return f'Reaction[id={self.id}, seen_date={self.seen_date}, reaction={self.reaction}, user={self.user}, quote_id={self.quote}]'


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session()
    user = User('3649028588457703', 'DAILY')
    session.add(user)
    quote = Quote("If you want to achieve greatness stop asking for permission.", "Anonymous")
    session.add(quote)
    session.commit()
    user_quote = Reaction('3649028588457703', quote.id, 'LIKE')
    session.add(user_quote)
    session.commit()
    session.close()
    print("=== Now querying data ===")
    session = Session()
    users = session.query(User).all()
    for user in users:
        print(user)
    quotes = session.query(Quote).all()
    for quote in quotes:
        print(quote)
    reactions = session.query(Quote.text).join(Reaction) \
        .filter(Reaction.reaction == 'LIKE')
    for reaction in reactions:
        print(reaction)
