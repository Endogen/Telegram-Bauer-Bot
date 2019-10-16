import bauer.constants as con
import bauer.emoji as emo
import bauer.utils as utl
import logging

from bismuthclient.bismuthutil import BismuthUtil
from bauer.plugins.wallet.wallet import Bismuth
from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Withdraw(BauerPlugin):

    BLCK_EXPL_URL = "https://bismuth.online/search?quicksearch="

    def __enter__(self):
        if not self.table_exists("withdraw"):
            sql = self.get_resource("create_withdraw.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.dependency
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        user = update.effective_user.username

        if len(args) < 2 or len(args) > 4:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        address = args[0]
        amount = args[1]

        operation = ""
        if len(args) > 2:
            operation = args[2]

        data = ""
        if len(args) > 3:
            data = args[3]

        # Check if provided amount is valid
        if not utl.is_numeric(amount) or float(amount) < 0:
            update.message.reply_text(
                text=f"{emo.ERROR} Specified amount is not valid",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check if provided address is valid
        if not BismuthUtil.valid_address(address):
            update.message.reply_text(
                text=f"{emo.ERROR} Provided address is not valid",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check if user has a wallet
        if not Bismuth.wallet_exists(user):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        message = update.message.reply_text(
            text=f"{emo.WAIT} Processing...",
            parse_mode=ParseMode.MARKDOWN)

        bis = Bismuth(user)
        bis.load_wallet()

        balance = bis.get_balance()
        total = float(amount) + con.TRX_FEE

        # Check for sufficient funds
        if not utl.is_numeric(balance) or float(balance) < total:
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Not enough funds")
            return

        try:
            # Execute withdrawing
            trx = bis.send(address, amount, operation, data)
        except Exception as e:
            error = f"Error withdrawing {amount} BIS " \
                    f"from @{user} " \
                    f"to {address} " \
                    f"with '{operation}' " \
                    f"and '{data}': {e}"
            logging.error(error)
            self.notify(error)
            trx = None

        if trx:
            logging.debug(
                f"Withdraw {amount} BIS "
                f"from @{user} "
                f"to {address} "
                f"with '{operation}' "
                f"and '{data}'")

            # Save withdrawing to database
            insert = self.get_resource("insert_withdraw.sql")
            self.execute_sql(insert, user, address, amount)

            url = f"{self.BLCK_EXPL_URL}{utl.encode_url(trx)}"

            # Send success message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.DONE} DONE!\n[View on Block Explorer]({url})\n"
                     f"(Available after ~1 minute)",
                parse_mode=ParseMode.MARKDOWN)
        else:
            # Send error message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Withdrawing not executed. Something went wrong...")
