import bauer.emoji as emo
import bauer.utils as utl
import bauer.constants as con
import logging

from telegram import ParseMode
from bauer.plugin import BauerPlugin
from bauer.plugins.wallet.wallet import Bismuth


class Tip(BauerPlugin):

    DEFAULT_TIP = 1  # BIS coins

    def __enter__(self):
        if not self.table_exists("tip"):
            sql = self.get_resource("create_tip.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.dependency
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        reply = update.message.reply_to_message

        # Tip the user that you reply to
        if reply:
            # Determine amount to tip
            if len(args) == 0:
                # Tip default BIS amount
                amount = self.DEFAULT_TIP
            elif len(args) == 1:
                # Tip specified BIS amount
                try:
                    amount = float(args[0])
                except:
                    msg = f"{emo.ERROR} Specified amount is not valid"
                    update.message.reply_text(msg)
                    return
            else:
                msg = "You are tipping the user you reply to. " \
                      "Only allowed argument is the amount."
                update.message.reply_text(msg)
                return

            to_user = reply.from_user.username

        # Provide username to be tipped
        else:
            if not args:
                msg = f"Usage:\n{self.get_usage()}"
                update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
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
                    msg = f"{emo.ERROR} Specified amount is not valid"
                    update.message.reply_text(msg)
                    return
            else:
                # Wrong syntax
                msg = f"{emo.ERROR} Wrong number of arguments:\n{self.get_usage()}"
                update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                return

            to_user = args[0]

            # Check if username starts with @
            if not to_user.startswith("@"):
                msg = f"{emo.ERROR} Username not valid:\n{self.get_usage()}"
                update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                return

            to_user = to_user[1:]

        from_user = update.effective_user.username

        # Check if sender has a wallet
        if not Bismuth.wallet_exists(from_user):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        # Check if recipient has a wallet
        if not Bismuth.wallet_exists(to_user):
            msg = f"{emo.ERROR} User @{utl.esc_md(to_user)} doesn't have a wallet yet"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        msg = f"{emo.WAIT} Processing..."
        message = update.message.reply_text(msg)

        # Init sender wallet
        bis = Bismuth(from_user)
        bis.load_wallet()

        # Check for sufficient funds
        balance = bis.get_balance()
        total = amount + con.TRX_FEE

        if not utl.is_numeric(balance) or float(balance) < total:
            msg = f"{emo.ERROR} Not enough funds"
            update.message.reply_text(msg)
            return

        # Process actual tipping
        if bis.tip(to_user, amount):
            # Save tipping in database
            insert = self.get_resource("insert_tip.sql")
            self.execute_sql(insert, from_user, to_user, amount)

            # Send success message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.DONE} @{utl.esc_md(to_user)} received `{amount}` BIS",
                parse_mode=ParseMode.MARKDOWN)

            try:
                # Get user ID from tipped user
                sql = self.get_resource("get_user_id.sql")
                res = self.execute_sql(sql, to_user, plugin="wallet")
                user_id = res["data"][0][0] if res["success"] else None

                if user_id:
                    # Send message to tipped user
                    msg = f"You've been tipped with `{amount}` BIS by @{utl.esc_md(from_user)}"
                    bot.send_message(user_id, msg, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logging.warning(e)
        else:
            # Send error message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Something went wrong")
