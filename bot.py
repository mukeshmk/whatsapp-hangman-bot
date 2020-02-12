import requests
from flask import Flask, request
from string import ascii_lowercase
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Initialize game state variables
count = -1
game_start = False
attempts_remaining = 6
word = ""
idxs = []
remaining_letters = 0
wrong_letters = []
word_solved = False

def init_word():
    global idxs, remaining_letters, wrong_letters, word_solved
    idxs = [letter not in ascii_lowercase for letter in word]
    remaining_letters = set(ascii_lowercase)
    wrong_letters = []
    word_solved = False

def init():
    global count, attempts_remaining, word, game_start
    count = -1
    game_start = False
    attempts_remaining = 6
    word = ""
    init_word()

@app.route('/bot', methods=['POST'])
def bot():
    # Initalizing global variables in function
    global count, attempts_remaining, word, game_start
    global idxs, remaining_letters, wrong_letters, word_solved

    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if 'start game' in incoming_msg and game_start == False:
        init()
        game_start = True

        msgbody = 'Starting a game of Hangman...\n'
        msgbody += 'Enter a Word: (_word: yourword_)'
    elif 'quit' in incoming_msg and game_start == True:
        init()

        msgbody = 'quiting game!'
    elif 'word: ' in incoming_msg and word == "" and game_start == True:
        word = incoming_msg.split(":")[1]
        init_word()
        count = 0

        msgbody = word
    elif len(incoming_msg) == 1 and count >= 0:
        msgbody = incoming_msg
    else:
        msgbody = "invalid cmd!"

    msg.body(msgbody)
    return str(resp)

# Run Server
if __name__ == '__main__':
    app.run()