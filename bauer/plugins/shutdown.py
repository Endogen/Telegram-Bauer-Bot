import threading
import bauer.emoji as emo

from bauer.plugin import BauerPlugin


class Shutdown(BauerPlugin):

    def get_handle(self):
        return "shutdown"

    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        msg = f"{emo.GOODBYE} Shutting down..."
        update.message.reply_text(msg)

        threading.Thread(target=self._shutdown_thread).start()

    def _shutdown_thread(self):
        self.tgb.updater.stop()
        self.tgb.updater.is_idle = False
