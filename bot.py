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
guessed_before = False

def init_word():
    global idxs, remaining_letters, wrong_letters, word_solved
    idxs = [letter not in ascii_lowercase for letter in word]
    remaining_letters = set(ascii_lowercase)
    wrong_letters = []
    word_solved = False

def init():
    global count, attempts_remaining, word, game_start, guessed_before
    count = -1
    game_start = False
    attempts_remaining = 6
    word = ""
    guessed_before = False
    init_word()

def get_display_word():
    global word, idxs
    if len(word) != len(idxs):
        raise ValueError('Word length and indices length are not the same')
    displayed_word = ''.join([letter if idxs[i] else '-' for i, letter in enumerate(word)])
    return displayed_word.strip()

def get_next_letter(msgbody):
    if len(remaining_letters) == 0:
        msgbody += 'There are no remaining letters\n'
        return msgbody
    msgbody += 'Choose the next letter:\n'
    return msgbody

def check_next_letter(msgbody, next_letter):
    global remaining_letters, guessed_before
    if len(next_letter) != 1:
        msgbody += '{0} is not a single character\n'.format(next_letter)
    elif next_letter not in ascii_lowercase:
        msgbody += '{0} is not a letter\n'.format(next_letter)
    elif next_letter not in remaining_letters:
        msgbody += '{0} has been guessed before\n'.format(next_letter)
        guessed_before = True
    else:
        remaining_letters.remove(next_letter)
    return msgbody

def game_state(msgbody):
    if attempts_remaining > 0 and not word_solved:
        # Print current game state
        msgbody += 'Word: {0}\n'.format(get_display_word())
        msgbody += 'Attempts Remaining: {0}\n'.format(attempts_remaining)
        msgbody += 'Previous Guesses: {0}\n'.format(' '.join(wrong_letters))
    return msgbody

def hangman(msgbody, next_letter):
    global attempts_remaining, idxs, remaining_letters, wrong_letters, word_solved

    if attempts_remaining > 0 and not word_solved:
        # Check if letter guess is in word
        if next_letter in word:
            # Guessed correctly
            msgbody += '{0} is in the word!\n'.format(next_letter)

            # Reveal matching letters
            for i in range(len(word)):
                if word[i] == next_letter:
                    idxs[i] = True
        else:
            # Guessed incorrectly
            msgbody += '{0} is NOT in the word!\n'.format(next_letter)

            # Decrement num of attempts left and append guess to wrong guesses
            attempts_remaining -= 1
            wrong_letters.append(next_letter)

        # Check if word is completely solved
        if False not in idxs:
            word_solved = True
            msgbody += 'The word is {0}\n'.format(word)
    return msgbody

@app.route('/bot', methods=['POST'])
def bot():
    # Initalizing global variables in function
    global count, attempts_remaining, word, game_start
    global idxs, remaining_letters, wrong_letters, word_solved, guessed_before

    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    msgbody = ""
    if ('hi' in incoming_msg.lower() or 'hello' in incoming_msg.lower()) and game_start == False:
        init()
        msgbody += "Hi! Let's play Hangman!\n"
        msgbody += "(to find out what I can do hit *cmd*)\n"
    elif 'cmd' in incoming_msg.lower() and game_start == False:
        init()
        msgbody += "*cmd*: to find out what I can do!\n"
        msgbody += "*start game*: to start game\n"
        msgbody += "*quit*: to quit the game at anypoint\n"
        msgbody += "*gl hf!* :)\n"
    elif ('start game' in incoming_msg.lower() or 'start' in incoming_msg.lower()) and game_start == False:
        init()
        game_start = True
        msgbody += 'Starting a game of Hangman!\n'
        msgbody += 'Enter a Word:\n'
        msgbody += '(in this format -> _word: yourword_)\n'
    elif 'quit' in incoming_msg.lower() and game_start == True:
        init()
        msgbody += 'quiting game!\n'
    elif 'word: ' in incoming_msg.lower() and word == "" and game_start == True:
        word = incoming_msg.split(":")[1]
        init_word()
        count = 0
        msgbody = game_state(msgbody)
        msgbody = get_next_letter(msgbody)
    elif len(incoming_msg) == 1 and count >= 0:
        count += 1
        if attempts_remaining <= 0:
            msgbody += 'The word is {0}\n'.format(word)
        else:
            msgbody = check_next_letter(msgbody, incoming_msg.lower())
            if not guessed_before:
                msgbody = hangman(msgbody, incoming_msg.lower())
            guessed_before = False
            msgbody = game_state(msgbody)
            if attempts_remaining > 0 and not word_solved:
                msgbody = get_next_letter(msgbody)
            elif attempts_remaining <= 0:
                msgbody += '*Booooo! You Lost!*\n'
                msgbody += 'The word is {0}\n'.format(word)
                msgbody += 'Quiting the game! Start again if you wanna play more!'
                init()
            elif word_solved:
                msgbody += '*Congratulations! You won!*\n'
                msgbody += 'Quiting the game! Start again if you wanna play more!'
                init()
    else:
        msgbody += "invalid cmd!\n"

    msg.body(msgbody)
    return str(resp)

# Run Server
if __name__ == '__main__':
    app.run()