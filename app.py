import json
import os
from typing import Tuple

from fbmessenger.quick_replies import QuickReplies, QuickReply
from flask import Flask, request

import actions

app = Flask(__name__)
app.debug = True

from fbmessenger import BaseMessenger, templates
from fbmessenger import elements


def send_quote_to_user(user_id, quote_text, quote_id):
    actions.mark_quote_as_seen(user_id, quote_id)
    quick_replies = QuickReplies([
        QuickReply(content_type="text",
                   title='Good one',
                   payload=f"like {quote_id}", ),
        QuickReply(content_type="text",
                   title='Not my taste',
                   payload=f"dislike {quote_id}", ),
    ])
    msg = elements.Text(text=quote_text, quick_replies=quick_replies)
    return messenger.send_msg(msg, user_id)


def send_user_subscribe_msg(user_id):
    if user_id is None:
        app.logger.warn('Trying to send a subscribe message without a user_id')
        return None

    # quick_replies = QuickReplies([
    #     QuickReply(content_type="text",
    #                title="Yes",
    #                payload=f"register {user_id}", ),
    #     QuickReply(content_type="text",
    #                title="No",
    #                payload=f"ignore {user_id}", ),
    # ])
    # msg = elements.DynamicText(text='Do you want to get daily quotes?',
    #                            quick_replies=quick_replies)
    btn1 = elements.Button(button_type='postback', title='Yes', payload=f"register {user_id}")
    btn2 = elements.Button(button_type='postback', title='No', payload=f"ignore {user_id}")
    elems = elements.Element(
        title='Do you want to get daily quotes',
        buttons=[btn1, btn2]
    )
    msg = templates.GenericTemplate(elements=[elems])
    return messenger.send_msg(msg, user_id)


def process_message_text(sender_id: str, text: str) -> str:
    app.logger.debug(f'Processing text from {sender_id}: {text}')
    response_text = None
    try:
        if text is None:
            return None
        elif text == 'help':
            response_text = """Type *register* to start getting quotes.
        Type *unregister* to stop getting quotes.
        Type *liked* to see quotes you liked.
        Type *help* to see this message."""
        elif text == 'liked':
            response_text = actions.get_liked_quotes(sender_id)
        elif text.startswith('register'):
            actions.register_user(sender_id)
            response_text = "You are now registered to get quotes"
        elif text.startswith('unregister') or text.startswith('ignore'):
            actions.remove_user(sender_id)
            response_text = "You won't get quotes anymore"
        elif text.startswith('like'):
            splitted = text.split(' ')
            actions.user_like(sender_id, splitted[1])
        elif text.startswith('dislike'):
            splitted = text.split(' ')
            actions.user_dislike(sender_id, splitted[1])
    except actions.ActionError as e:
        pass
    return response_text


def process_message(payload: any) -> Tuple[str, str]:
    app.logger.debug('payload received: {}'.format(payload))
    if 'sender' not in payload:
        return None, None
    sender_id = payload['sender']['id']
    message = payload['message']
    message_text = message['text'] if 'text' in message else None
    if message_text == 'hi':
        send_user_subscribe_msg(sender_id)
        return None, None
    if 'quick_reply' in message:
        message_text = message['quick_reply']['payload']
    response_text = process_message_text(sender_id, message_text)
    return response_text, sender_id


class Messenger(BaseMessenger):
    def __init__(self, page_access_token, app_secret=None):
        super().__init__(page_access_token, app_secret)

    def message(self, message):
        response_text, recepient_id = process_message(message)
        if response_text is not None:
            res = self.send_text(response_text, recepient_id)
            app.logger.debug('Response from sending text: {}'.format(res))

    def postback(self, message):
        sender_id = message['sender']['id']
        postback_text = message['postback']['payload']
        response_text = process_message_text(sender_id, postback_text)

    def get_sender_id(self, payload):
        for entry in payload['entry']:
            if 'messaging' not in entry:
                continue
            for message in entry['messaging']:
                if message.get("is_echo") is True:
                    break
                return message['sender']['id']

    def send_msg(self, msg, recepient_id):
        return self.client.send(msg.to_dict(),
                                recepient_id,
                                'RESPONSE',
                                notification_type='REGULAR',
                                timeout=None, tag=None)

    def send_text(self, text, recepient_id):
        app.logger.info(f'Sending: msg="{text}" recepient={recepient_id} ==> not sending')
        if text is None or recepient_id is None:
            return None
        msg = elements.DynamicText(text=text)
        return self.send_msg(msg, recepient_id)


FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN', 'quotesapp')
messenger = Messenger(FB_PAGE_TOKEN)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == FB_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        payload = request.get_json(force=True)
        sender = messenger.get_sender_id(payload)
        app.logger.info(f'Got message from {sender}: {payload}')
        messenger.handle(payload)
    return '', 200


@app.route('/get-users', methods=['GET'])
def get_users():
    users = actions.get_registered_users()
    response = dict()
    response['users'] = [user.__repr__() for user in users]
    return json.dumps(response)


@app.route('/send-quote/<user_id>', methods=['GET'])
def send_quote(user_id: str):
    users = actions.get_registered_users()
    user = next(filter(lambda user: user.user_id == user_id, users), None)
    if user is None:
        return 'User does not exist', 404
    quote_id, quote_text = actions.suggest_quote_for_user(user_id)
    res = send_quote_to_user(user_id, quote_text, quote_id)
    return res, 200


if __name__ == "__main__":
    if FB_VERIFY_TOKEN is None or FB_PAGE_TOKEN is None:
        print('''Environment variables FB_VERIFY_TOKEN and FB_PAGE_TOKEN should be set
in order to start this program. exiting...''')
        exit(1)
    app.run(host='0.0.0.0')
