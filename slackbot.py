import os
import time
import re
import urllib2
import logging
import datetime
import socket
import sys
import signal
import json
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from slackclient import SlackClient
from user_info import UserInfo
from jenkins_job_commands import JenkinsJobCommands
from bot import Bot


AT_BOT_ID = ""
AT_BOT_NAME = ""

state = dict(
    title='slackbot',
    version='1.0.0',
    shutdown=False,
    ecs=dict()
)

class SlackbotHealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/serverStatus':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(state))
        if self.path:
            self.send_response(200)
            self.end_headers()
            self.wfile.write('<html><body><h1>Welcome to jenkins-bot</h1></body></html>')

    def do_HEAD(self):
        if self.path == '/serverStatus':
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


class Slackbot(Bot):

    def __init__(self, sc, chat_data):
        """
            Main slackbot code
        """
        Bot.__init__(self, sc, chat_data)
        #print("inside Constructor() Method")
        self.slack_client = sc
        self.data = chat_data

        if chat_data['text'].startswith(AT_BOT_ID):
            self.command = chat_data['text'].split(AT_BOT_ID)[1].strip()
        elif chat_data['text'].startswith(AT_BOT_NAME):
            self.command = chat_data['text'].split(AT_BOT_NAME)[1].strip()
        else:
            self.command = chat_data['text'].split(AT_BOT_NAME)[1].strip()

        self.channel = chat_data['channel']


    def handle_command(self):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
            :return:
        """
        #print("inside handle_command() Method")
        if self.command.startswith("jenkins"):
                JenkinsJobCommands(self.slack_client, self.data, self.command).handle_jenkinscommands()
        elif self.command.startswith("help"):
                super(Slackbot, self).display_help()
        elif self.command.startswith("details"):
                message = "My IP is: " + socket.gethostbyname(socket.gethostname())
                self.slack_client.api_call("chat.postMessage", channel=self.channel, text=message, as_user=True)
        
        else:
            response = "unknown command"
            self.slack_client.api_call("chat.postMessage", channel=self.channel, text=response, as_user=True)
            super(Slackbot, self).display_help()

    
def parse_slack_output(client):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    #print("inside parse_slack_output() Method")
    input_list = client.rtm_read()
    if input_list:
        for input in input_list:
            if input and 'text' in input:
                if input['text'].startswith(AT_BOT_ID) or input['text'].startswith(AT_BOT_NAME):
                    logging.info(input['text'])
                    return input
    return None


def logging_setup(SLACK_BOT_NAME):
    """
        setup logging for project
        :return:
    """
    #print("inside logging_setup() Method")
    dirName = 'logs/'

    if not os.path.exists(dirName):
        os.mkdir(dirName)

    logging.basicConfig(filename= dirName + SLACK_BOT_NAME + '-' + datetime.datetime.now().strftime('%m_%d_%Y-%H_%M_%S') + '.log',
        level=logging.DEBUG)
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s] %(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    #logging.info('Started')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """


def start(server_class=ThreadedHTTPServer, handler_class=SlackbotHealthCheckHandler, port=8080):
    """
        start slackbot
    """
    server_address = ('', port)

    httpd = server_class(server_address, handler_class)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.setdaemon = True

    try:
        server_thread.start()
    
        SLACK_BOT_NAME = 'jenkins-bot'
        SLACK_BOT_TOKEN = "xoxb-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        SLACK_BOT_ID = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        global AT_BOT_ID 
        AT_BOT_ID = "<@" + SLACK_BOT_ID + ">"
        global AT_BOT_NAME 
        AT_BOT_NAME = "<@" + SLACK_BOT_NAME + ">"

        logging_setup(SLACK_BOT_NAME)
        slack_client = SlackClient(SLACK_BOT_TOKEN)
        logging.info("starting bot: " + SLACK_BOT_NAME )
        user_info = UserInfo(SLACK_BOT_ID, slack_client)
        if user_info.online:
            time.sleep(5)
            logging.error('Another instance of ' + SLACK_BOT_NAME + ' bot is already running. '
                      'You must close the other instance first!')
            exit(-1)

        connect = False
        while True:
            if not connect:
                connect = slack_client.rtm_connect()
                logging.info("connecting to rtm, bot: " + SLACK_BOT_NAME)
                logging.info("connecting to rtm, bot: " + AT_BOT_NAME + ', Id: ' + AT_BOT_ID)
                logging.info('rtm_connect: ' + str(connect))
                if connect:
                    logging.info("Slackbot connected and running!")
                else:
                    logging.error("Connection failed. Invalid Slack token or bot ID?")
                    time.sleep(1)

            if connect:
                try:
                     # Parse any slack input
                    data = parse_slack_output(slack_client)
                    if data:
                        Slackbot(slack_client, data).handle_command()
                    
                except Exception:
                    logging.error('exception', exc_info=True)
                    time.sleep(1)
                    connect = False

    except KeyboardInterrupt:
        logging.info('caught KeyboardInterrupt')
        state['shutdown'] = True
        

    if state['shutdown']:
        httpd.shutdown()


if __name__ == "__main__":
    start()
