import boto3
import boto3.dynamodb
from boto3.dynamodb.conditions import Key, Attr
import uuid
import urllib
import os

#setup this function to use an alexa skill

def lambda_handler(event, context):

    if event.has_key('session'):
        if event['session']['application']['applicationId']==os.environ['appid']:
            if event["request"]["type"] == "LaunchRequest":
                return on_launch(event["request"], event["session"])
            elif event["request"]["type"] == "IntentRequest":
                print 'Intent Request'
                print event
                print context
                s = on_intent(event["request"]["intent"], event["session"])
                print s
                return s
            elif event["request"]["type"] == "SessionEndedRequest":
                return on_session_ended(event["request"], event["session"])
        else:
            raise 400
            #should return an http 400 - need to check this out
    else:
        #not from alexa
        raise ValueError(event)

def on_intent(intent_request, session):

    print intent_request["name"]
    if intent_request["name"] == "PlayRandomClip":
        print 'Playing Random Clip'
        return PlayClip('unknown')
    elif intent_request["name"] == "PlayClipFrom":
        print intent_request
        #small fix for sometimes seeing random in show name
        show_name = intent_request['slots']['AMAZON.TVSeries']['value']
        show_name = show_name.lower()
        if show_name == 'random':
            show_name = 'unknown'
        return PlayClip(show_name)
    else:
        raise ValueError(intent_request)

def handle_session_end_request():
    card_title = "Thanks for using this skill."
    speech_output = "Thanks for using this skill."
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, '', None, should_end_session))


def on_session_ended(session_ended_request, session):
    return handle_session_end_request()
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return GetWelcomeResponse()

def GetWelcomeResponse():
    card_title = 'Sound Board'
    speech_output = 'Welcome to the totally random sound board!'
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def SessionEndedRequest():
    card_title = 'Sound Board'
    speech_output = 'Goodbye for now, cruel world'
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def build_speechlet_response(title, output, filename, reprompt_text, should_end_session):
    s =  {
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "token": "12345",
                            "url": filename,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ],
            "shouldEndSession": should_end_session
        }
    }
    return s

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
}

def PlayClip(showname):

    print

    #get data from
    show_name = showname
    print('PlayClip - show: {0}'.format(show_name))
    title = "Soundboard " + show_name
    text = "Playing a file from " + show_name
    end_session = True

    #query dynamo for the file
    dynamo = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamo.Table("soundboard")
    s = str(uuid.uuid4())
    response = table.query(KeyConditionExpression=Key('show').eq(show_name) & Key('uuid').gt(s))
    print 'Checking GT: {0} / {1}'.format(show_name, s)
    items = response['Items']
    print items
    if len(items) == 0:
        print 'Checking LT: {0} / {1}'.format(show_name, s)
        response = table.query(KeyConditionExpression=Key('show').eq(show_name) & Key('uuid').lt(s))
        items = response['Items']
        if len(items)==0:
            #nothing to do - generate a better error message
            print items
            print('did not find any shows')
            return couldNotFind(show_name)
    print(items)
    filename = os.environ['s3bucket'] + urllib.pathname2url(items[0]['filename'])
    return build_speechlet_response(title, text, filename, "", True)

def couldNotFind(show_name):
    #basic response
    returntext = "I could not find any clips for {0}".format(show_name)

    s = {"version": "1.0",
            "response": {
            "outputSpeech": {
                "type": "Sound Board",
                "text": returntext,
                },
            "card": {
                "type": "Standard",
                "title": "Soundboard",
                "content": "",
                "text": returntext,
                },
            "shouldEndSession": True,
            }
        }

    return s
