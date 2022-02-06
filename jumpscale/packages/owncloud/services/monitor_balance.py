import os
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j

MAIL_QUEUE = "MAIL_QUEUE"
EMAIL = os.environ.get("ALERT_EMAIL")

class BalanceChecker(BackgroundService):
    def __init__(self, interval=10 * 60, *args, **kwargs):
        """10mins  (10 * 60)
        needs mail server configurations to be set in j.config
        'EMAIL_SERVER_CONFIG':
        {   
            'host': 'smtp.gmail.com',
            'port': '587',
            'username': 'testhammamw2010@gmail.com',
            'password': ''
        }
        """
        super().__init__(interval=interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        j.logger.debug("balance checker service started")
        balance = j.tools.http.get("http://localhost:3001/balance").json().get("balance")

        if float(balance) > 1000:
            j.logger.debug(f"balance {balance} is ok. service finished")
            return
        message = f"Owncloud deployment wallet is about to empty it has only {balance} TFTs, please transfer some TFTs in it"
        j.logger.critical(message)
        mail_info = {
            "recipients_emails": EMAIL,
            "sender": "no-reply@threefold.io",
            "subject": "Owncloud deployer wallet alert",
            "message": message,
        }
        j.core.db.rpush(MAIL_QUEUE, j.data.serializers.json.dumps(mail_info))

service = BalanceChecker()