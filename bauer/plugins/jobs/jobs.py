import bauer.emoji as emo
import bauer.utils as utl

from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Jobs(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if len(args) < 1:
            update.message.reply_text(
                text=self.get_usage(),
                parse_mode=ParseMode.MARKDOWN)
            return

        command = args[0].lower().strip()

        # ------ LIST JOBS ------
        if command == "list":
            jobs = self.get_jobs()

            if not jobs or len(jobs) < 1:
                msg = f"{emo.INFO} No jobs found"
                update.message.reply_text(msg)
                return

            msg = "*Available Jobs*\n\n"

            for job in self.get_jobs():
                msg += f"{job.name}\n"
            update.message.reply_text(
                text=msg,
                parse_mode=ParseMode.MARKDOWN)
            return

        if len(args) < 2:
            update.message.reply_text(
                text=self.get_usage(),
                parse_mode=ParseMode.MARKDOWN)
            return

        plugin = args[1].lower().strip()
        job = self.get_job(name=plugin)

        if not job:
            msg = f"{emo.ERROR} Job not found"
            update.message.reply_text(msg)
            return

        # ------ START JOB ------
        if command == "start":
            if job.enabled:
                msg = f"{emo.INFO} Job already running"
                update.message.reply_text(msg)
                return

            # Enable repeating job
            job.enabled = True

            msg = f"{emo.DONE} Job started"
            update.message.reply_text(msg)

        # ------ STOP JOB ------
        elif command == "stop":
            if not job.enabled:
                msg = f"{emo.INFO} Job already stopped"
                update.message.reply_text(msg)
                return

            # Disable repeating job
            job.enabled = False

            msg = f"{emo.DONE} Job stopped"
            update.message.reply_text(msg)

        # ------ RUN JOB ------
        elif command == "run":
            job.run(bot)

            msg = f"{emo.DONE} Job executed"
            update.message.reply_text(msg)

        # ------ STATE OF JOB ------
        elif command == "state":
            state = "enabled" if job.enabled else "disabled"

            update.message.reply_text(
                text=f"Job is *{state}*",
                parse_mode=ParseMode.MARKDOWN)

        # ------ INTERVAL OF JOB ------
        elif command == "interval":
            if len(args) > 2:
                interval = args[2].lower().strip()

                if utl.is_numeric(interval):
                    job.interval = int(interval)

                    msg = f"{emo.DONE} New interval set"
                    update.message.reply_text(msg)

        else:
            update.message.reply_text(
                text=self.get_usage(),
                parse_mode=ParseMode.MARKDOWN)
