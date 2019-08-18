import os
import json
import logging
import bauer.constants as con
import urllib.parse as ul

from bismuthclient.bismuthclient import BismuthClient


class Bismuth:

    TERMS_FILE = "terms.md"

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
        os.makedirs(con.DER_DIR, exist_ok=True)
        return os.path.join(con.DER_DIR, f"{username}.der")

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

    @staticmethod
    def url_encode_trxid(trxid):
        return ul.quote_plus(trxid)

    @staticmethod
    def get_terms():
        terms_file = os.path.join(con.RES_DIR, Bismuth.TERMS_FILE)
        with open(terms_file, "r", encoding="utf8") as file:
            content = file.readlines()

        return "".join(content)
