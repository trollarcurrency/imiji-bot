import aiohttp
import socket
from config import Config

class RPCClient(object):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls) -> 'RPCClient':
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.node_url = Config.instance().node_url
            cls.node_port = Config.instance().node_port
            cls.wallet_id = Config.instance().wallet
            cls.ipv6 = '::' in cls.node_url
            cls.connector = aiohttp.TCPConnector(family=socket.AF_INET6 if cls.ipv6 else socket.AF_INET,resolver=aiohttp.AsyncResolver())
            cls.session = aiohttp.ClientSession(connector=cls.connector)
        return cls._instance


    @classmethod
    async def close(cls):
        if hasattr(cls, 'session') and cls.session is not None:
            await cls.session.close()
        if cls._instance is not None:
            cls._instance = None

    async def make_request(self, req_json: dict):
        async with self.session.post("http://{0}:{1}".format(self.node_url, self.node_port),json=req_json, timeout=300) as resp:
            return await resp.json()

    async def account_create(self) -> str:
        account_create = {
            'action': 'account_create',
            'wallet': self.wallet_id
        }
        respjson = await self.make_request(account_create)
        if 'account' in respjson:
            return respjson['account']
        return None

    async def account_balance(self, account: str) -> dict:
        account_balance = {
            'action': 'account_balance',
            'account': account
        }
        respjson = await self.make_request(account_balance)
        if 'balance' in respjson:
            return respjson
        return None

    async def send(self, id: str, source: str, destination: str, amount: str) -> str:
        """Make transaction, return hash if successful"""
        send_action = {
            'action': 'send',
            'wallet': Config.instance().wallet,
            'source': source,
            'destination': destination,
            'amount': amount,
            'id': id
        }
        respjson = await self.make_request(send_action)
        if 'block' in respjson:
            return respjson['block']
        return None