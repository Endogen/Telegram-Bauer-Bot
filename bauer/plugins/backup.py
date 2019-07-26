import os
import os.path
import zipfile
import time

import bauer.emoji as emo
import bauer.constants as con

from bauer.plugin import BauerPlugin


class Backup(BauerPlugin):

    def get_handle(self):
        return "backup"

    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        # List of folders to exclude from backup
        exclude = [con.LOG_DIR, con.BCK_DIR, "__pycache__"]

        # Create 'backup' folder
        os.makedirs(os.path.join(os.getcwd(), con.BCK_DIR), exist_ok=True)

        filename = os.path.join(con.BCK_DIR, f"{time.strftime('%Y%m%d%H%M%S')}.zip")
        with zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            bck_base_dir = os.path.abspath(os.path.join(f"'.'{os.sep}", con.BCK_DIR))
            base_path = os.path.normpath(bck_base_dir)

            base_dir = os.path.abspath('./')
            for root, dirs, files in os.walk(base_dir, topdown=True):
                dirs[:] = [d for d in dirs if d not in exclude and not d.startswith(".")]
                for name in sorted(dirs):
                    path = os.path.normpath(os.path.join(root, name))
                    zf.write(path, os.path.relpath(path, base_path))
                for name in files:
                    path = os.path.normpath(os.path.join(root, name))
                    if os.path.isfile(path):
                        zf.write(path, os.path.relpath(path, base_path))

        bot.send_document(
            chat_id=update.effective_user.id,
            caption=f"{emo.DONE} Backup created",
            document=open(os.path.join(base_dir, filename), 'rb'))
