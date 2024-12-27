import requests

from contracts.default import Default
from utils.get_abi import get_abi
from utils.encode import get_data_byte64

from decimal import Decimal


class StakeStone(Default):
    def __init__(self, account):
        super().__init__(account.private_key, "https://eth.llamarpc.com/", get_abi("StakeStone"), "0x2aCA0C7ED4d5EB4a2116A3bc060A2F264a343357", account.proxy)

    def stake(self, amount):
        data = self.contract.encode_abi("depositETH", args=(
            self.address,
        ))

        tx = {
            "chainId": self.w3.eth.chain_id,
            "from": self.address,
            "to": "0x2aCA0C7ED4d5EB4a2116A3bc060A2F264a343357",
            "value": hex(self.gwei_to_wei(amount)),
            "data": data,
            "maxFeePerGas": "0x10642ac00",
            "maxPriorityFeePerGas": "0x10642ac00",
            "nonce": self.nonce()
        }

        tx.update({"gas": hex(int(self.w3.eth.estimate_gas(tx) * 1.5))})

        return self.send_transaction(tx, "stake eth")

    def referal(self, code):
        resp = self.session.post(f"https://points.stakestone.io/bera/gWithCode", json={"address": self.address, "refCode": code})
        return resp.json()
