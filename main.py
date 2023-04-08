import logging
import time
import uuid
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="")
channel_id = ""
logger = logging.getLogger(__name__)

class Thread:
    def __init__(self, channel_id, client, thread_ts):
        self.channel_id = channel_id
        self.client = client
        self.thread_ts = thread_ts
    def send_message(self, text):
        self.client.chat_postMessage(
            channel=self.channel_id,
            text=text,
            client_msg_id=str(uuid.uuid4()),
            thread_ts=self.thread_ts
        )
    def get_latest(self):
        response = self.client.conversations_replies(
            channel=self.channel_id,
            ts=self.thread_ts,
        )
        messages = response.get("messages", [])
        return messages[-1]["text"]

class ThreadBuilder:
    def __init__(self, channel_id, client):
        self.channel_id = channel_id
        self.client = client
    def create_new(self, text):
        response = self.client.chat_postMessage(
            channel=self.channel_id,
            text=text,
            client_msg_id=str(uuid.uuid4()),
        )
        return Thread(self.channel_id, self.client, response["ts"])
    def from_ts(self, ts):
        return Thread(self.channel_id, self.client, ts) 

