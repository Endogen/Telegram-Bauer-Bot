import bauer.emoji as emo
import bauer.utils as utl

from telegram import ParseMode
from bauer.plugin import BauerPlugin, Category
from bauer.plugins.wallet.bismuth import Bismuth


class Tip(BauerPlugin):

    DEFAULT_TIP = 1

    def __enter__(self):
        if not self.table_exists("tip"):
            sql = self.get_resource("create_tip.sql")
            self.execute_sql(sql)
        return self

    def get_handle(self):
        return "tip"

    @BauerPlugin.threaded
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
            try:
                amount = float(args[1])
            except:
                update.message.reply_text(
                    text=f"{emo.ERROR} Specified amount is not valid",
                    parse_mode=ParseMode.MARKDOWN)
                return
        else:
            # Wrong syntax
            update.message.reply_text(
                text=f"{emo.ERROR} Wrong number of arguments:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        to_user = args[0]

        # Check if username starts with @
        if not to_user.startswith("@"):
            update.message.reply_text(
                text=f"{emo.ERROR} Username not valid:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        to_user = to_user[1:]
        from_user = update.effective_user["username"]

        # Check if sender has a wallet
        if not Bismuth.wallet_exists(from_user):
            update.message.reply_text(
                text=f"{emo.ERROR} Create a wallet first with:\n`/wallet create`",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Check if recipient has a wallet
        if not Bismuth.wallet_exists(to_user):
            update.message.reply_text(
                text=f"{emo.ERROR} User @{utl.esc_md(to_user)} doesn't have a wallet",
                parse_mode=ParseMode.MARKDOWN)
            return

        message = update.message.reply_text(f"{emo.WAIT} Processing...")

        # Init sender wallet
        bis = Bismuth(from_user)
        bis.load_wallet()

        # Check for sufficient funds
        if float(bis.get_balance()) <= amount:
            update.message.reply_text(f"{emo.ERROR} Not enough funds")
            return

        # Process actual tipping
        if bis.tip(to_user, amount):
            # Save tipping in database
            statement = self.get_resource("insert_tip.sql")
            self.execute_sql(statement, from_user, to_user, amount)

            # Send success message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.DONE} @{to_user} received `{amount}` BIS",
                parse_mode=ParseMode.MARKDOWN)
        else:
            # Send error message
            bot.edit_message_text(
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
