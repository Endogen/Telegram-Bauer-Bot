import os
import os.path
import zipfile
import time

import bauer.emoji as emo
import bauer.constants as con

from bauer.plugin import BauerPlugin


# TODO: Add possibility to add argument <plugin name> to backup / export a plugin
class Backup(BauerPlugin):

    BCK_DIR = "backups"

    @BauerPlugin.threaded
    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        # List of folders to exclude from backup
        exclude = [con.DIR_LOG, self.BCK_DIR, "__pycache__"]

        plugin = self.plugin_name()
        bck_path = os.path.join(con.DIR_SRC, con.DIR_PLG, plugin, self.BCK_DIR)

        # Create folder to store backups
        os.makedirs(bck_path, exist_ok=True)

        filename = os.path.join(bck_path, f"{time.strftime('%Y%m%d%H%M%S')}.zip")
        with zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            bck_base_dir = os.path.abspath(os.path.join(f"'.'{os.sep}", bck_path))
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
