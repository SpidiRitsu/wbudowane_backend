import yagmail
import datetime
import sys

EMAIL = 'doorbell.wbudowane@gmail.com'
PASSWORD = 'Wbudowane2019'

yag = yagmail.SMTP(EMAIL, PASSWORD)

receiver = EMAIL
subject = "🚨🚨🚨 Motion DETECTED! 🚨🚨🚨"
body = """<div style='color: #e50606; font-size: 20px;'>🚨 <strong style="font-size: 24px;">Date and time:</strong> """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """ 🚨</div>"""

def send_motion_notification(photo):
	yag.send(to=receiver, subject=subject, contents=[body, {photo: 'Camera_Feed'}])

if __name__ == "__main__":
	send_motion_notification(sys.argv[1])