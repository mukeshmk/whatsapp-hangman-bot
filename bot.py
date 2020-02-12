import requests
from flask import Flask, request
from string import ascii_lowercase
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Initialize game state variables
count = 0
attempts_remaining = 6
word = ""

idxs = [letter not in ascii_lowercase for letter in word]
remaining_letters = set(ascii_lowercase)
wrong_letters = []
word_solved = False

def init():
    global count, attempts_remaining, word
    global idxs, remaining_letters, wrong_letters, word_solved

    count = 0
    attempts_remaining = 6
    word = ""

    idxs = [letter not in ascii_lowercase for letter in word]
    remaining_letters = set(ascii_lowercase)
    wrong_letters = []
    word_solved = False

@app.route('/bot', methods=['POST'])
def bot():
    # Initalizing global variables in function
    global count, attempts_remaining, word
    global idxs, remaining_letters, wrong_letters, word_solved

    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if 'start game' in incoming_msg:
        init()

        msgbody = 'Starting a game of Hangman...\n'
        msgbody += 'Enter a Word: (word: *your word*)'

        msg.body(msgbody)
    elif 'quit' in incoming_msg:
        init()

        msgbody = 'quiting game!'
        
        msg.body(msgbody)
    elif 'word: ' in incoming_msg:
        word = incoming_msg.split(":")[1]
        msgbody = word

        msg.body(msgbody)
        
    return str(resp)

# Run Server
if __name__ == '__main__':
    app.run()