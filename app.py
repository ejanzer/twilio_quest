import os

from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

recordings = []

# Render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle a POST request to send a text message. This is called via ajax
# on our web page
@app.route('/message', methods=['POST'])
def message():
    # Send a text message to the number provided
    message = client.sms.messages.create(to=request.form['to'],
                                         from_=TWILIO_NUMBER,
                                         body='Good luck on your Twilio quest!')

    # Return a message indicating the text message is enroute
    return 'Message on the way!'

# Handle a POST request to make an outbound call. This is called via ajax
# on our web page
@app.route('/call', methods=['POST'])
def call():
    # Make an outbound call to the provided number from your Twilio number
    call = client.calls.create(to=request.form['to'], from_=TWILIO_NUMBER, 
                               url='http://twimlets.com/message?Message%5B0%5D=http://demo.kevinwhinnery.com/audio/zelda.mp3')

    # Return a message indicating the call is coming
    return 'Call inbound!'

# Generate TwiML instructions for an outbound call
@app.route('/hello')
def hello():
    response = twiml.Response()
    response.say('Hello there! You have successfully configured a web hook.')
    response.say('Good luck on your Twilio quest!', voice='woman')
    return Response(str(response), mimetype='text/xml')

@app.route('/handle_key1', methods=['GET', 'POST'])
def handle_key1():
    #Handle first key press from user.
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        response = twiml.Response()
        response.say('Hello there! You are #1!')
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "2"    :
        response = twiml.Response()
        response.say('Hello there! You are Slitherin!')
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "3":
        response = twiml.Response()
        response.say("Leave a message!")
        response.record(maxLength="30", action="/handle-recording")
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "4":
        response = twiml.Response()
        if recordings == []:
            response.say("There are no recorded messages.")
        else: response.play(recordings[-1])
        return Response(str(response), mimetype='text/xml')
    else:
        response = twiml.Response()
        response.say('Goodbye.')
        return Response(str(response), mimetype='text/xml')

@app.route('/handle-recording', methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get("RecordingUrl", None)
    recordings.append(recording_url)
    response = twiml.Response()
    response.say("Thanks for hissing. Listen to what you hissed.")
    response.play(recording_url)
    response.say("Goodbye.") 
    return Response(str(response), mimetype='text/xml')


@app.route('/incoming/call')
def incoming_call():
    response = twiml.Response()
    with response.gather(numDigits=1, action="/handle_key1", method="POST") as g:
        g.say('Press 1 for operator, 2 for a SNAKE!, 3 for leave a message, 4 to hear the last message.')

    return Response(str(response), mimetype='text/xml')

@app.route('/incoming/sms')
def incoming_sms():
    response = twiml.Response()
    response.sms('What is black, white and red all over?')
    return Response(str(response), mimetype='text/xml')

if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)