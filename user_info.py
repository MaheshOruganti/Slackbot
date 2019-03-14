"""
UserInfo
"""
import logging

class UserInfo(object):
    """
    Class to get user info from slack
    api_call = self.slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('id') == self.user_id:
                print user
                response = "Hey " + user['name']
                self.slack_client.api_call("chat.postMessage", channel=self.channel, text=response, as_user=True)
                response = "your email is " + user['profile']['email']
                self.slack_client.api_call("chat.postMessage", channel=self.channel, text=response, as_user=True)
    """
    def __init__(self, user_id, slack_client):
        self.user_id = user_id
        self.slack_client = slack_client
        api_call = slack_client.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('id') == self.user_id:
                    self.user = user


    @staticmethod
    def get_id_from_name(slack_client, name):
        """
        Gets the id from a slack users name
        :param slack_client:
        :param name:
        :return:
        """
        api_call = slack_client.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user['name'] == name:
                    return user.get('id')
        return None

    def details(self):
        """
        Will log details of the user
        :return:
        """
        logging.info(self.user)


    def presence(self):
        """
        Will get the users presence
        :return:
        """
        return self.slack_client.api_call("users.getPresence?user="+self.user_id)


    @property
    def online(self):
        """
        Will get all users that are online
        """
        api_call = self.presence()
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            return api_call.get('online')
        return None


    @property
    def name(self):
        """
        gets users name
        :return:
        """
        return self.user['name']


    @property
    def email(self):
        """
        get users email
        :return:
        """
        return self.user['profile']['email']
