import bauer.constants as con
import bauer.emoji as emo
import bauer.utils as utl
import logging
import random
import math

from bauer.plugins.wallet.wallet import Bismuth
from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Rain(BauerPlugin):

    def __enter__(self):
        if not self.table_exists("rain"):
            sql = self.get_resource("create_rain.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.dependency
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # command <total amount> <number of users>
        if len(args) == 2:
            amount = args[0]
            users = args[1]

        # command <total amount>/<number of users>
        elif len(args) == 1 and "/" in args[0]:
            lst = args[0].split("/")
            if len(lst) == 2:
                amount = lst[0]
                users = lst[1]
            else:
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
                return
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Make sure that 'amount' and 'users' are valid values
        try:
            amount = float(amount)
            users = int(users)
        except:
            msg = f"{emo.ERROR} Arguments not valid"
            update.message.reply_text(msg)
            return

        if users < 1:
            msg = f"{emo.ERROR} You have to rain on at least one user"
            update.message.reply_text(msg)
            return

        multiplier = 10 ** 2
        user_amount = math.floor(amount / users * multiplier) / multiplier

        if user_amount < 0.01:
            msg = f"{emo.ERROR} Amount per user to small. Has to be at least `0.01`"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        from_user = update.effective_user.username
        from_user_id = update.effective_user.id

        # Check if sender has a wallet
        if not Bismuth.wallet_exists(from_user):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        # Get all users from database
        sql = self.get_resource("read_users.sql")
        res = self.execute_sql(sql, plugin="wallet")

        if not res["success"]:
            msg = f"{emo.ERROR} Not possible to retrieve users"
            update.message.reply_text(msg)

            error = res["data"]
            logging.error(error)
            self.notify(error)
            return

        # Remove own user from list of users to rain on
        user_list = [x for x in res["data"] if x[1] != from_user]

        # Check if enough users available to be rained on
        if len(user_list) < users:
            msg = f"{emo.ERROR} Not enough users. {len(user_list)} available"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        # Randomly choose users from all users
        chosen = random.sample(user_list, users)

        msg = f"{emo.WAIT} Processing..."
        message = update.message.reply_text(msg)

        # Init sender wallet
        bis = Bismuth(from_user)
        bis.load_wallet()

        balance = bis.get_balance()
        total = amount + (users * con.TRX_FEE)

        # Check for sufficient funds
        if not utl.is_numeric(balance) or float(balance) < total:
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Not enough funds")
            return

        result = f"{emo.DONE} @{utl.esc_md(from_user)} sent `{user_amount}` BIS each to: "

        for to_data in chosen:
            to_user_id = to_data[0]
            to_user = to_data[1]

            try:
                # Execute tipping
                trx = bis.tip(to_user, user_amount)
            except Exception as e:
                error = f"Error executing rain from @{from_user} to @{to_user} with {user_amount} BIS: {e}"
                logging.error(error)
                self.notify(error)
                trx = None

            if trx:
                logging.debug(f"Rain from '{from_user}' to '{to_user}' with {user_amount} BIS - TRX: {trx}")

                # Save tipping to database
                # TODO: Do i have to lock the DB while writing?
                insert = self.get_resource("insert_rain.sql")
                self.execute_sql(insert, from_user, to_user, amount)

                # Add username of tipped user to confirmation message
                result += f"@{utl.esc_md(to_user)} "

                try:
                    # Send success message to tipped user
                    msg = f"You've been tipped with `{user_amount}` BIS by @{utl.esc_md(from_user)}"
                    bot.send_message(to_user_id, msg, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    error = f"Not possible to notify user '{to_user}' about rain"
                    logging.debug(f"{error}: {e}")
            else:
                try:
                    # Send error message to tipping user
                    msg = f"{emo.ERROR} Not possible to send `{user_amount}` BIS to @{utl.esc_md(to_user)}"
                    bot.send_message(from_user_id, msg, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    error = f"Not possible to notify tipping user '{from_user}' about failed rain"
                    logging.debug(f"{error}: {e}")

        # Check if at least one user got tipped
        if result.count("@") > 1:
            # TODO: Use 'split_msg' from utils here
            # Send success message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=result,
                parse_mode=ParseMode.MARKDOWN)
        else:
            # Send error message
            bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"{emo.ERROR} Rain not executed. Something went wrong...")
