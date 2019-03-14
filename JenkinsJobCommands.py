"""
JenkinsJobCommands
"""
import urllib2
import urllib
import json
from bot import Bot

class JenkinsJobCommands(Bot):
		""" 
				Class to govern available commands for running tests 
		"""
		def __init__(self, slack_client, data, command):
				Bot.__init__(self, slack_client, data)
				self.slack_client = slack_client
				self.command = command
				self.data = data
				self.channel = data['channel']
				

		def handle_jenkinscommands(self):
				"""
						Handles the commands
				"""
				if self.command.lower() == 'jenkins help':
						self.display_help()
				else:
						self.run_jenkinsJob()


		def run_jenkinsJob(self):
				"""
						Will kick off jenkins job
						:return:
				"""
				#print(self.user_info.name)
				params = {}
				headers = {"authorization": "Basic XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
									 "cache-control": "no-cache",
									 "jenkins-crumb": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
									 "postman-token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}
				# Note: please change jenkins server url and parameters based on your project/requirements.
			
				url = "https://jenkins.com/buildWithParameters" + \
							"?PROJECT=" + self.projectName + "&ENV=" + self.env + "&DEVICE=" + device + "&SLACK_CHANNEL="+ self.channel + \
							"&TEST=" + self.test+ ""
					req = urllib2.Request(url, params, headers)
					urllib2.urlopen(req)
					super(VenusJobCommands, self).post_message("kicked off Project: " + self.projectName + " for Device: " + device)


		def display_help(self):
				"""
						Displays help
				"""
				bot_name = "jenkins-bot"
				message = "Usage:\r\n" \
									"\t@" + bot_name + " jenkins <projectName> <env> <device> <test> \r\n"
				super(JenkinsJobCommands, self).post_message(message)
