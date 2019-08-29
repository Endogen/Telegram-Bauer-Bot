import bauer.emoji as emo

from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Feedback(BauerPlugin):

    def __enter__(self):
        if not self.table_exists("feedback"):
            sql = self.get_resource("create_feedback.sql")
            self.execute_sql(sql)
        return self

    def get_handle(self):
        return "feedback"

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        user = update.message.from_user
        if user.username:
            name = f"@{user.username}"
        else:
            name = user.first_name

        feedback = update.message.text.replace(f"/{self.get_handle()} ", "")

        for admin in self.cfg_get("admin", "ids", plugin=False):
            bot.send_message(admin, f"Feedback from {name}: {feedback}")

        update.message.reply_text(f"Thanks for letting us know {emo.TOP}")

        sql = self.get_resource("insert_feedback.sql")
        self.execute_sql(sql, user.id, name, user.username, feedback)

    def get_usage(self):
        return f"`/{self.get_handle()} <your feedback>`\n"

    def get_description(self):
        return "Send us your feedback"

    def get_category(self):
        return Category.BOT
