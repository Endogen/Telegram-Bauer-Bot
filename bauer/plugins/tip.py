import bauer.emoji as emo
import bauer.utils as utl

from telegram import ParseMode
from bauer.plugin import BauerPlugin, Category
from bauer.bismuth import Bismuth


class Tip(BauerPlugin):

    DEFAULT_TIP = 1

    def get_handle(self):
        return "tip"

    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Determine amount to tip
        if len(args) == 1:
            # Tip default BIS amount
            amount = self.DEFAULT_TIP
        elif len(args) == 2:
            # Tip specified BIS amount
            amount = args[1]

            if not utl.is_number(amount):
                update.message.reply_text(
                    text=f"{emo.ERROR} Specified amount is not valid",
                    parse_mode=ParseMode.MARKDOWN)
                return
        else:
            # Wrong syntax
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        to_user = args[0]

        if not to_user.startswith("@"):
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        to_user = to_user[1:]
        from_user = update.effective_user["username"]

        # Check if sender has a wallet
        if not Bismuth.wallet_exists(from_user):
            update.message.reply_text(
                text=f"No wallet yet, create one with\n`/wallet create`",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check if recipient has a wallet
        if not Bismuth.wallet_exists(to_user):
            update.message.reply_text(
                text=f"User @{utl.esc_md(to_user)} doesn't have a wallet",
                parse_mode=ParseMode.MARKDOWN)
            return

        message = update.message.reply_text(f"{emo.WAIT} Processing...")

        bis = Bismuth(from_user)
        bis.load_wallet()

        if bis.tip(to_user, amount):
            self.tgb.updater.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.CHECK} DONE!")
        else:
            self.tgb.updater.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Something went wrong")

    def get_usage(self):
        return f"`/{self.get_handle()} <@username> <amount>`\n" \
               f"`/{self.get_handle()} <@username>`"

    def get_description(self):
        return "Tip BIS coins to user"

    def get_category(self):
        return Category.BISMUTH
