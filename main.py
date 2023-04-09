import logging
import time
import uuid
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import asyncio
import aiohttp
import subprocess
import html

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = AsyncWebClient(token="")
channel_id = ""
logger = logging.getLogger(__name__)

class Thread:
    def __init__(self, channel_id: str, client: AsyncWebClient, thread_ts: str):
        self.channel_id = channel_id
        self.client = client
        self.thread_ts = thread_ts
        self.latest_ts = thread_ts
    async def send_message(self, text: str) -> None:
        response = await self.client.chat_postMessage(
            channel=self.channel_id,
            text=text,
            client_msg_id=str(uuid.uuid4()),
            thread_ts=self.thread_ts
        )
        self.latest_ts = response["ts"]
    async def send_message_and_wait(self, text: str, wait_time: int = 3) -> str: 
        await self.send_message(text)
        while True:
            await asyncio.sleep(wait_time)
            latest = await self.get_latest()
            if latest[0] != self.latest_ts:
                self.latest_ts = latest[0]
                return latest[1]
    async def get_latest(self) -> tuple:
        response = await self.client.conversations_replies(
            channel=self.channel_id,
            ts=self.thread_ts,
        )
        messages = response.get("messages", [])
        return (messages[-1]["ts"], messages[-1]["text"])
    async def wait_reply(self, wait_time: int = 3) -> str:
        while True:
            await asyncio.sleep(wait_time)
            latest = await self.get_latest()
            if latest[0] != self.latest_ts:
                self.latest_ts = latest[0]
                return latest[1]

class ThreadBuilder:
    def __init__(self, channel_id: str, client: AsyncWebClient) -> None:
        self.channel_id = channel_id
        self.client = client
    async def create_new(self, text: str) -> Thread:
        response = await self.client.chat_postMessage(
            channel=self.channel_id,
            text=text,
            client_msg_id=str(uuid.uuid4()),
        )
        return Thread(self.channel_id, self.client, response["ts"])
    def from_ts(self, ts: str) -> Thread:
        return Thread(self.channel_id, self.client, ts) 
