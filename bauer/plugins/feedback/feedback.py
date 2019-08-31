import bauer.emoji as emo

from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Feedback(BauerPlugin):

    def __enter__(self):
        if not self.table_exists("feedback"):
            sql = self.get_resource("create_feedback.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        user = update.message.from_user
        if user.username:
            name = f"@{user.username}"
        else:
            name = user.first_name

        feedback = update.message.text.replace(f"/{self.handle()} ", "")

        for admin in self.cfg_get("admin", "ids", plugin=False):
            bot.send_message(admin, f"Feedback from {name}: {feedback}")

        update.message.reply_text(f"Thanks for letting us know {emo.HEART}")

        sql = self.get_resource("insert_feedback.sql")
        self.execute_sql(sql, user.id, name, user.username, feedback)
