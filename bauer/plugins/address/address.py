from bauer.plugins.wallet.wallet import Bismuth
from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Address(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        username = update.effective_user.username

        if not Bismuth.wallet_exists(username):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        address = Bismuth.get_address_for(username)

        update.message.reply_text(
            text=f"Your BIS address is `{address}`",
            parse_mode=ParseMode.MARKDOWN)
