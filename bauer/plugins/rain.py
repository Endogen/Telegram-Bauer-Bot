from bauer.plugin import BauerPlugin, Category
from telegram import ParseMode
from bauer.config import ConfigManager as Cfg


class Rain(BauerPlugin):

    def __enter__(self):
        # TODO: Remove the check and move it to BauerPlugin or TelegramBot after DB methods exposed
        if Cfg.get("database", "use_db"):
            if not self.tgb.db.table_exists("rain"):
                statement = self.tgb.db.get_sql("create_rain")
                self.tgb.db.execute_sql(statement)
        return self

    def get_handle(self):
        return "rain"

    @BauerPlugin.save_user
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # TODO: Implement

    def get_usage(self):
        return f"`/{self.get_handle()}`"

    def get_description(self):
        return "Rain BIS coins"

    def get_category(self):
        return Category.BISMUTH
