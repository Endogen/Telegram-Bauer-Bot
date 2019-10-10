import bauer.emoji as emo
import bauer.utils as utl

from bismuthclient.bismuthutil import BismuthUtil
from bauer.plugins.wallet.wallet import Bismuth
from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Withdraw(BauerPlugin):

    BLCK_EXPL_URL = "https://bismuth.online/search?quicksearch="

    @BauerPlugin.threaded
    @BauerPlugin.dependency
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        username = update.effective_user.username

        if not Bismuth.wallet_exists(username):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        if len(args) < 2 or len(args) > 4:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        send_to = args[0]
        amount = args[1]

        operation = ""
        if len(args) > 2:
            operation = args[2]

        data = ""
        if len(args) > 3:
            data = args[3]

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

        bis = Bismuth(username)
        bis.load_wallet()
        trx = bis.send(send_to, amount, operation, data)

        url = f"{self.BLCK_EXPL_URL}{utl.encode_url(trx)}"

        if trx:
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.DONE} Done!\n[View on Block Explorer]({url})\n"
                     f"(Available after ~1 minute)",
                parse_mode=ParseMode.MARKDOWN)
        else:
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Not able to send Transaction")
