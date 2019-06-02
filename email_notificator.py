import yagmail
import datetime

EMAIL = 'doorbell.wbudowane@gmail.com'
PASSWORD = 'Wbudowane2019'

yag = yagmail.SMTP(EMAIL, PASSWORD)

receiver = EMAIL
subject = "🔔🔔🔔 Doorbell ACTIVATION! 🔔🔔🔔"
body = """<div style='color: #FF7F11; font-size: 20px;'>🔔 <strong style="font-size: 24px;">Date and time:</strong> """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """ 🔔</div>"""

def send_doorbell_notification():
	yag.send(to=receiver, subject=subject, contents=body)