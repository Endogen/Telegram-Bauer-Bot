import os
import json
import logging
import bauer.constants as con

from bismuthclient.bismuthclient import BismuthClient


class Bismuth:

    MODULE = str(__name__).split(".")[-1]
    WALLET_DIR = os.path.join(con.DIR_SRC, con.DIR_PLG, MODULE, "wallets")

    def __init__(self, username):
        logging.debug(f"Create Bismuth client for user {username}")
        self._client = self._get_client(username)
        logging.debug(f"Get Bismuth server for user {username}")
        server = self._client.get_server()
        logging.debug(f"Current server {server}")

    def _get_client(self, username):
        wallet_path = self.get_wallet_path(username)
        client = BismuthClient(wallet_file=wallet_path)
        return client

    def load_wallet(self):
        c = self._client
        c.new_wallet(wallet_file=c.wallet_file)
        c.load_wallet(wallet_file=c.wallet_file)

    def get_balance(self):
        return self._client.balance(for_display=True)

    def get_address(self):
        return self._client.address

    def tip(self, username, amount):
        address = Bismuth.get_address_for(username)
        return self._client.send(address, amount) if address else None

    def send(self, send_to, amount):
        return self._client.send(send_to, float(amount))

    @staticmethod
    def get_wallet_path(username):
        os.makedirs(Bismuth.WALLET_DIR, exist_ok=True)
        return os.path.join(Bismuth.WALLET_DIR, f"{username}.der")

    @staticmethod
    def get_address_for(username):
        if Bismuth.wallet_exists(username):
            try:
                wallet = Bismuth.get_wallet_path(username)
                with open(wallet, "r") as f:
                    return json.load(f)["Address"]
            except Exception as e:
                logging.error(e)
                return None
        else:
            return None

    @staticmethod
    def wallet_exists(username):
        wallet = Bismuth.get_wallet_path(username)
        return os.path.isfile(wallet)
