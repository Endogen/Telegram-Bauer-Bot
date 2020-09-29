import logging
import bauer.emoji as emo
import bauer.utils as utl

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from bauer.plugins.wallet.wallet import Bismuth
from bismuthclient.bismuthutil import BismuthUtil
from bauer.plugin import BauerPlugin


class Bisurl(BauerPlugin):

    BLCK_EXPL_URL = "https://bismuth.online/search?quicksearch="

    def __enter__(self):
        self.add_handler(CallbackQueryHandler(self._callback), group=1)

        if not self.table_exists("bisurl"):
            sql = self.get_resource("create_bisurl.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.dependency
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if len(args) == 0:
            msg = f"Usage:\n{self.get_usage()}"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        username = update.effective_user.username

        # Check if user has a wallet
        if not Bismuth.wallet_exists(username):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        try:
            decode = BismuthUtil.read_url(args[0])
        except Exception as e:
            msg = f"{emo.ERROR} Does not look like a proper BIS URL"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            logging.error(f"{msg}: {e}")
            return

        amount = float(decode['amount'])
        address = decode['recipient']
        operation = decode['operation']
        message = decode['openfield']
        fees = BismuthUtil.fee_for_tx(message)

        # Check if provided address is valid
        if not BismuthUtil.valid_address(address):
            update.message.reply_text(
                text=f"{emo.ERROR} Provided address is not valid",
                parse_mode=ParseMode.MARKDOWN)
            return

        bisurl_id = self.unix_time()

        # Save transaction to database
        insert = self.get_resource("insert_bisurl.sql")
        self.execute_sql(insert, bisurl_id, username, address, amount, operation, message)

        msg = "Execute following transaction?\n\n"
        msg += "▸ Recipient: {}\n".format(address)
        msg += "▸ Amount: {:.2f} BIS\n".format(amount)
        msg += "▸ Operation: {}\n".format(operation)
        msg += "▸ Message: {}\n".format(message)
        msg += "▸ Fees: {} BIS\n".format(fees)

        update.message.reply_text(msg, reply_markup=self._keyboard(bisurl_id))

    def _keyboard(self, bisurl_id):
        menu = utl.build_menu([InlineKeyboardButton("Execute", callback_data=bisurl_id)])
        return InlineKeyboardMarkup(menu, resize_keyboard=True)

    def _callback(self, bot, update):
        query = update.callback_query
        username = update.effective_user["username"]

        sql = self.get_resource("select_bisurl.sql")
        res = self.execute_sql(sql, query.data)

        user = res["data"][0][1]
        address = res["data"][0][2]
        amount = res["data"][0][3]
        operation = res["data"][0][4]
        message = res["data"][0][5]

        if user == username:
            msg = f"{emo.WAIT} Processing..."
            bot.answer_callback_query(query.id, msg)

            bis = Bismuth(user)
            bis.load_wallet()

            try:
                # Execute sending transaction via BISURL
                trx = bis.send(address, amount, operation, message)
            except Exception as e:
                error = f"Error sending via BISURL {amount} BIS " \
                        f"from @{user} " \
                        f"to {address} " \
                        f"with operation '{operation}' " \
                        f"and message '{message}': {e}"
                logging.error(error)
                trx = None

            if trx:
                logging.debug(
                    f"Sent via BISURL {amount} BIS "
                    f"from @{user} "
                    f"to {address} "
                    f"with operation '{operation}' "
                    f"and message '{message}'")

                url = f"{self.BLCK_EXPL_URL}{utl.encode_url(trx)}"

                # Send success message
                query.edit_message_text(
                    f"{emo.DONE} DONE!\n[View on Block Explorer]({url})\n"
                    f"(Available after ~1 minute)",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                # Send error message
                query.edit_message_text(
                    f"{emo.ERROR} Sending via BISURL not executed. Something went wrong...")
        else:
            msg = f"{emo.ERROR} Wrong user"
            bot.answer_callback_query(query.id, msg)

    def unix_time(self, date_time=None, millis=True):
        from datetime import datetime

        if not date_time:
            date_time = datetime.utcnow()

        seconds = (date_time - datetime(1970, 1, 1)).total_seconds()
        return int(seconds * 1000 if millis else seconds)
