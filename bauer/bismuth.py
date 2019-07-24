import os
import json
import logging
import bauer.constants as con

from bismuthclient.bismuthclient import BismuthClient


class Bismuth:

    def __init__(self, username):
        self._client = self._get_client(username)
        self._client.get_server()

    def _get_client(self, username):
        wallet_path = self.get_wallet_path(username)
        client = BismuthClient(wallet_file=wallet_path)
        return client

    @staticmethod
    def get_wallet_path(username):
        return os.path.join(con.DAT_DIR, f"{username}.der")

    def load_wallet(self):
        c = self._client
        c.new_wallet(wallet_file=c.wallet_file)
        c.load_wallet(wallet_file=c.wallet_file)

    def get_balance(self):
        return self._client.balance(for_display=True)

    def get_address(self):
        return self._client.address

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

    def tip(self, username, amount):
        address = Bismuth.get_address_for(username)
        return self._client.send(address, amount) if address else None

    def send(self, send_to, amount):
        return self._client.send(send_to, float(amount))

    @staticmethod
    def wallet_exists(username):
        wallet = Bismuth.get_wallet_path(username)
        return os.path.isfile(wallet)

    @staticmethod
    def convert_trxid(trxid):
        # TODO: Which other characters do i have to replace?
        return trxid.replace("+", "%2B")

    @staticmethod
    def get_terms():
        return "Generated wallet is meant to be for tipping and should only " \
               "hold small amounts of coins. Bismuth developers have access " \
               "to the private key of the address."

    @staticmethod
    def terms_accepted(username):
        # TODO: Save to DB that user accepted
        pass
