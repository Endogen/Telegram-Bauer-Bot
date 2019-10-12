import bauer.constants as con
import bauer.utils as utl
import bauer.emoji as emo
import logging
import json
import os

from telegram.ext import CallbackQueryHandler
from bismuthclient.bismuthclient import BismuthClient
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bauer.plugin import BauerPlugin


class Wallet(BauerPlugin):

    TERMS_FILE = "terms.md"

    def __enter__(self):
        self.add_handler(CallbackQueryHandler(self._callback))

        if not self.table_exists("terms_accepted"):
            sql = self.get_resource("create_terms.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        username = update.effective_user.username

        if not username:
            msg = "You need to have an username to create a wallet"
            update.message.reply_text(msg)
            return

        if Bismuth.wallet_exists(username):
            update.message.reply_text(
                text=f"{emo.INFO} Wallet already created",
                parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_text(
            text=self.get_resource(self.TERMS_FILE),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self._terms_keyboard(username))

    def _terms_keyboard(self, username):
        menu = utl.build_menu([InlineKeyboardButton("Accept Terms", callback_data=username)])
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        query = update.callback_query
        user_id = update.effective_user["id"]
        username = update.effective_user["username"]

        if query.data == username:
            msg = f"{emo.WAIT} Wait a few seconds..."
            bot.answer_callback_query(query.id, msg)

            query.edit_message_text(
                f"{emo.WAIT} Generating wallet...",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=None)

            # Save user id and username to database
            statement = self.get_resource("insert_terms.sql")
            self.execute_sql(statement, user_id, username)

            try:
                bis = Bismuth(username)
                bis.load_wallet()
            except Exception as e:
                logging.error(e)
                self.notify(e)
                bis = None

            if bis:
                msg = f"Hey @{utl.esc_md(username)}, your address is `{bis.get_address()}`"
                query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
            else:
                msg = f"{emo.ERROR} Something went wrong..."
                query.edit_message_text(msg)


class Bismuth:

    MODULE = str(__name__).split(".")[-1]
    WALLET_DIR = os.path.join(con.DIR_SRC, con.DIR_PLG, MODULE, "wallets")

    def __init__(self, username):
        self._client = self._get_client(username)
        self._client.get_server()

    def _get_client(self, username):
        wallet_path = self._wallet_path(username)
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
        return self._client.send(address, float(amount)) if address else None

    def send(self, address, amount, operation="", data=""):
        return self._client.send(address, float(amount), operation=operation, data=data)

    @staticmethod
    def _wallet_path(username):
        os.makedirs(Bismuth.WALLET_DIR, exist_ok=True)
        return os.path.join(Bismuth.WALLET_DIR, f"{username}.der")

    @staticmethod
    def get_address_for(username):
        if Bismuth.wallet_exists(username):
            try:
                wallet = Bismuth._wallet_path(username)
                with open(wallet, "r") as f:
                    return json.load(f)["Address"]
            except Exception as e:
                logging.error(e)
                return None
        else:
            return None

    @staticmethod
    def wallet_exists(username):
        wallet = Bismuth._wallet_path(username)
        return os.path.isfile(wallet)
