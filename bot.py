"""
Bot - Parent class 
        
"""
from user_info import UserInfo

class Bot(object):
    def __init__(self, slack_client, data):
        self.channel = data['channel']

        if 'user' in data:
            self.user_info = UserInfo(data['user'], slack_client)
            self.user_name = self.user_info.name
        else:
            self.user_info = None

    def display_help(self):
        """
            Displays help
        """
        bot_name = "jenkins-bot"
        message = "Usage:\r\n" \
                    "\t@" + bot_name + " help \r\n" \
                    "\t@" + bot_name + " details\r\n" \
                    "\t@" + bot_name + " jenkins help \r\n"

        self.post_message(message)


    def post_message(self, message):
        """
            Posts message to slack channel
            :param message:
            :return:
        """
        self.slack_client.api_call("chat.postMessage", channel=self.channel, text=message, as_user=True)


    def response_username(self):
        """
            gets the username to respond to, if the are an actual user then respond @username else webhook
            :return:
        """
        if self.user_info:
            response = "@" + self.user_name
        else:
            response = "webhook"
        return response


