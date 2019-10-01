import bauer.constants as con
import os

from MyQR import myqr
from bauer.plugins.wallet.wallet import Bismuth
from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Deposit(BauerPlugin):

    BIS_LOGO = "logo.png"
    QRCODES_DIR = "qr_codes"

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        username = update.effective_user.username

        if not Bismuth.wallet_exists(username):
            msg = "Accept terms and create a wallet first with:\n/accept"
            update.message.reply_text(msg)
            return

        qr_dir = os.path.join(self.get_plg_path(), self.QRCODES_DIR)
        os.makedirs(qr_dir, exist_ok=True)

        qr_name = f"{username}.png"
        qr_code = os.path.join(qr_dir, qr_name)

        address = Bismuth.get_address_for(username)

        if not os.path.isfile(qr_code):
            logo = os.path.join(self.get_plg_path(), con.DIR_RES, self.BIS_LOGO)

            myqr.run(
                address,
                version=1,
                level='H',
                picture=logo,
                colorized=True,
                contrast=1.0,
                brightness=1.0,
                save_name=qr_name,
                save_dir=qr_dir)

        with open(qr_code, "rb") as qr_pic:
            update.message.reply_photo(
                photo=qr_pic,
                caption=f"`{address}`",
                parse_mode=ParseMode.MARKDOWN)
