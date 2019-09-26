import bauer.constants as con
import bauer.utils as utl
import bauer.emoji as emo
import logging
import json
import os

from MyQR import myqr
from bismuthclient.bismuthutil import BismuthUtil
from telegram.ext import CallbackQueryHandler
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bismuthclient.bismuthclient import BismuthClient
from bauer.plugin import BauerPlugin


# TODO: Combine all Bismuth commands to one '/bauer' command?
class Bismuth(BauerPlugin):

    BIS_LOGO = "logo.png"
    TERMS_FILE = "terms.md"
    QRCODES_DIR = "qr_codes"
    BLCK_EXPL_URL = "https://bismuth.online/search?quicksearch="

    def __enter__(self):
        self._tgb.dispatcher.add_handler(
            CallbackQueryHandler(self._callback))
        if not self.table_exists("terms"):
            sql = self.get_resource("create_terms.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        username = update.effective_user.username

        if not username:
            msg = "You need to set a username to use this bot"
            update.message.reply_text(msg)
            return

        args = [s.lower() for s in args]
        arg = args[0]

        # ---- CREATE WALLET ----
        if arg == "create":
            if BisClient.wallet_exists(username):
                update.message.reply_text(
                    text=f"{emo.INFO} Wallet already created",
                    parse_mode=ParseMode.MARKDOWN)
                return

            terms_file = os.path.join(self.get_res_path(), self.TERMS_FILE)
            with open(terms_file, "r", encoding="utf8") as file:
                update.message.reply_text(
                    text=file.read(),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self._terms_keyboard(username))

        # ---- SHOW ADDRESS ----
        elif arg == "address":
            if not self._wallet_exists(update, username):
                return

            address = BisClient.get_address_for(username)

            update.message.reply_text(
                text=f"Your BIS address is `{address}`",
                parse_mode=ParseMode.MARKDOWN)

        # ---- DEPOSIT ----
        elif arg == "deposit":
            if not self._wallet_exists(update, username):
                return

            qr_dir = os.path.join(self.get_plg_path(), self.QRCODES_DIR)
            qr_name = f"{username}.png"
            qr_code = os.path.join(qr_dir, qr_name)

            address = BisClient.get_address_for(username)

            if not os.path.isfile(qr_code):
                logo = os.path.join(con.DIR_RES, self.BIS_LOGO)

                myqr.run(
                    address,
                    version=1,
                    level='H',
                    picture=logo,
                    colorized=True,
                    contrast=1.0,
                    brightness=1.0,
                    save_name=qr_name,
                    save_dir=qr_dir)

            with open(qr_code, "rb") as qr_pic:
                update.message.reply_photo(
                    photo=qr_pic,
                    caption=f"`{address}`",
                    parse_mode=ParseMode.MARKDOWN)

        # ---- WITHDRAW ----
        # TODO: Add optional data
        elif arg == "withdraw":
            if not self._wallet_exists(update, username):
                return

            if len(args) != 3:
                # TODO: Add better description
                # TODO: Create .md file for that
                update.message.reply_text(
                    text=f"{emo.ERROR} Wrong syntax\n"
                         f"`/{self.get_handle()} withdraw <address> <amount>`",
                    parse_mode=ParseMode.MARKDOWN)
                return

            send_to = args[1]
            amount = args[2]

            if not BismuthUtil.valid_address(send_to):
                update.message.reply_text(
                    text=f"{emo.ERROR} Bismuth address is not valid",
                    parse_mode=ParseMode.MARKDOWN)
                return

            if not utl.is_numeric(amount) or float(amount) < 0:
                update.message.reply_text(
                    text=f"{emo.ERROR} Specified amount is not valid",
                    parse_mode=ParseMode.MARKDOWN)
                return

            message = update.message.reply_text(
                text=f"{emo.WAIT} Sending...",
                parse_mode=ParseMode.MARKDOWN)

            bis = BisClient(username)
            bis.load_wallet()
            trx = bis.send(send_to, amount)

            url = f"{self.BLCK_EXPL_URL}{utl.url_encode(trx)}"

            if trx:
                self._tgb.updater.bot.edit_message_text(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    text=f"{emo.DONE} Done! [View on Block Explorer]({url})\n"
                         f"(Available after ~1 minute)",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                self._tgb.updater.bot.edit_message_text(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    text=f"{emo.ERROR} Not able to send Transaction")

        # ---- BALANCE ----
        elif arg == "balance":
            if not self._wallet_exists(update, username):
                return

            message = update.message.reply_text(
                text=f"{emo.WAIT} Checking balance...",
                parse_mode=ParseMode.MARKDOWN)

            bis = BisClient(username)
            bis.load_wallet()

            balance = bis.get_balance()

            if utl.is_numeric(balance):
                balance = f"`{balance}` BIS"

            self._tgb.updater.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"Balance: {balance}",
                parse_mode=ParseMode.MARKDOWN)

        # ---- Everything else ----
        else:
            update.message.reply_text(
                text=f"{emo.ERROR} Wrong sub-command:\n"
                     f"{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)

    def _wallet_exists(self, update, username):
        if not BisClient.wallet_exists(username):
            update.message.reply_text(
                text=f"Create a wallet first with:\n`/{self.get_handle()} create`",
                parse_mode=ParseMode.MARKDOWN)
            return False
        return True

    def _terms_keyboard(self, username):
        menu = utl.build_menu([InlineKeyboardButton("Accept Terms", callback_data=username)])
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        query = update.callback_query
        username = update.effective_user["username"]

        if query.data == username:
            self._terms_accepted(username)

            query.edit_message_text(
                f"{emo.WAIT} Generating wallet...",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=None)

            try:
                bis = BisClient(username)
                bis.load_wallet()
            except Exception as e:
                logging.error(e)
                self.notify(e)
                bis = None

            if bis:
                query.edit_message_text(
                    f"Hey @{utl.esc_md(username)}, your address is `{bis.get_address()}`",
                    parse_mode=ParseMode.MARKDOWN)
                bot.answer_callback_query(query.id, text=f"{emo.HEART} Wallet created")
            else:
                query.edit_message_text(f"{emo.ERROR} Something went wrong...")
                bot.answer_callback_query(query.id, text=f"{emo.ERROR} No wallet created")

    def _terms_accepted(self, username):
        """ Add flag that user accepted terms """
        statement = self.get_resource("insert_terms.sql")
        self.execute_sql(statement, username, 1)


class BisClient:

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
        address = BisClient.get_address_for(username)
        return self._client.send(address, amount) if address else None

    def send(self, send_to, amount):
        return self._client.send(send_to, float(amount))

    @staticmethod
    def get_wallet_path(username):
        os.makedirs(BisClient.WALLET_DIR, exist_ok=True)
        return os.path.join(BisClient.WALLET_DIR, f"{username}.der")

    @staticmethod
    def get_address_for(username):
        if BisClient.wallet_exists(username):
            try:
                wallet = BisClient.get_wallet_path(username)
                with open(wallet, "r") as f:
                    return json.load(f)["Address"]
            except Exception as e:
                logging.error(e)
                return None
        else:
            return None

    @staticmethod
    def wallet_exists(username):
        wallet = BisClient.get_wallet_path(username)
        return os.path.isfile(wallet)
