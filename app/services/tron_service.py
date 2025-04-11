import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.trongrid.io"

async def get_wallet_info(address: str) -> dict:
    headers = {
        "TRON-PRO-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(f"{BASE_URL}/wallet/getaccount", json={
            "address": address,
            "visible": True
        }) as resp:
            account_data = await resp.json()

        async with session.post(f"{BASE_URL}/wallet/getaccountresource", json={
            "address": address,
            "visible": True
        }) as resp:
            resource_data = await resp.json()

        balance = account_data.get("balance", 0)
        freeNetUsed = resource_data.get("freeNetUsed", 0)
        freeNetLimit = resource_data.get("freeNetLimit", 0)
        energyUsed = resource_data.get("EnergyUsed", 0)
        energyLimit = resource_data.get("EnergyLimit", 0)

        return {
            "balance_trx": balance,
            "bandwidth_remaining": freeNetLimit - freeNetUsed,
            "energy_remaining": energyLimit - energyUsed
        }
