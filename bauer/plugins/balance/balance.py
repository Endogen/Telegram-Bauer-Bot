import bauer.emoji as emo
import bauer.utils as utl

from bauer.plugins.wallet.wallet import Bismuth
from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Balance(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.dependency
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        username = update.effective_user.username

        if not Bismuth.wallet_exists(username):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        message = update.message.reply_text(
            text=f"{emo.WAIT} Checking balance...",
            parse_mode=ParseMode.MARKDOWN)

        bis = Bismuth(username)
        bis.load_wallet()

        balance = bis.get_balance()

        if utl.is_numeric(balance):
            balance = f"`{balance}` BIS"

        self._tgb.updater.bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text=f"Balance: {balance}",
            parse_mode=ParseMode.MARKDOWN)
