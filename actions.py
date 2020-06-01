import json
from typing import Tuple

from db.models import *

session = Session()


class ActionError(Exception):
    pass


def _update_user_status(user_id, status):
    if status not in FREQUENCY_OPTIONS:
        raise ActionError(f'user status must be one of {FREQUENCY_OPTIONS}')
    user = session.query(User).get(user_id)
    if user is None:
        user = User(user_id, status)
        session.add(user)
    user.frequency = status
    session.commit()


def mark_quote_as_seen(user_id: str, quote_id: int):
    reaction = Reaction(user_id, quote_id, 'SEEN')
    session.add(reaction)
    session.commit()


def _update_reaction(user_id, quote_id, latest_reaction):
    if latest_reaction not in REACTIONS_OPTIONS:
        raise ActionError(f'reaction must be one of {REACTIONS_OPTIONS}')
    user = session.query(User).get(user_id)
    if user is None:
        raise ActionError(f'User {user_id} not found')
    quote = session.query(Quote).get(quote_id)
    if quote is None:
        raise ActionError(f'Quote {quote_id} not found')

    reaction = session.query(Reaction) \
        .filter(Reaction.user == user_id,
                Reaction.quote == quote_id).first()
    if reaction is None:
        reaction = Reaction(user_id, quote_id, reaction)
        session.add(reaction)
        quote.seen_count += 1
    reaction.seen_date = datetime.now().date()
    reaction.reaction = latest_reaction
    if latest_reaction == 'LIKE':
        quote.like_count += 1
    else:
        quote.dislike_count += 1
    session.commit()


def register_user(user_id):
    _update_user_status(user_id, 'DAILY')


def remove_user(user_id):
    _update_user_status(user_id, 'NEVER')


def user_like(user_id, quote_id):
    _update_reaction(user_id, quote_id, 'LIKE')


def user_dislike(user_id, quote_id):
    _update_reaction(user_id, quote_id, 'DISLIKE')


def suggest_new_quote(text, author):
    quote = Quote(text, author)
    session.add(quote)
    session.commit()


def get_liked_quotes(user_id):
    user = session.query(User).get(user_id)
    if user is None:
        raise ActionError(f'User {user_id} not found')
    liked_quotes = session.query(Quote) \
        .join(Reaction) \
        .filter(Reaction.reaction == 'LIKE', Reaction.user == user_id) \
        .all()
    return '\n'.join(quote.as_text() for quote in liked_quotes)


def get_registered_users():
    users = session.query(User).filter(User.frequency != 'NEVER').all()
    return users


def suggest_quote_for_user(user_id: str) -> Tuple[int, str]:
    quotes_user_saw = session \
        .query(Reaction.quote) \
        .filter(Reaction.user == user_id)
    quote = session.query(Quote) \
        .filter(Quote.id.notin_(quotes_user_saw)).first()
    return (quote.id, quote.as_text()) if quote is not None else (None, None)


if __name__ == '__main__':
    # liked_quotes = get_liked_quotes('3649028588457703')
    # print(liked_quotes)
    quote_id, suggested_quote = suggest_quote_for_user('3649028588457703')
    print(suggested_quote)
