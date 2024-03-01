import aiohttp
from utils import logger

logger = logger.setup_logger("handler")

class AsyncQueryRequestor():
    def __init__(self, base_url, email, api_key):
        self.base_url = base_url
        self.headers =   {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.auth = aiohttp.BasicAuth(email, api_key)

    async def get(self, endpoint):
        url = f"https://{self.base_url}/rest/api/3/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, auth=self.auth) as response:
                    return await response.json()
        except aiohttp.ClientConnectorError as e:
            logger.error(e)
            
    async def post(self, endpoint, payload):
        url = f"https://{self.base_url}/rest/api/3/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, auth=self.auth, data=payload) as response:
                    return await response.json()
        except aiohttp.ClientConnectorError as e:
            logger.error(e)
            
    
    async def put(self, endpoint, payload):
        url = f"https://{self.base_url}/rest/api/3/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=self.headers, auth=self.auth, data=payload) as response:
                    return await response.json()
        except:
            logger.error(e)
