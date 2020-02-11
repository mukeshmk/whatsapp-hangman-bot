from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

count = 0

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    global count

    msg.body(str(count))
    count+=1
    return str(resp)

# Run Server
if __name__ == '__main__':
    app.run()