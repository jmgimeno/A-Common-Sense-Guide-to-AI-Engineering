import os
from dotenv import load_dotenv
import yagmail

load_dotenv()

send_to_email = "person.email.is.being.sent.to@gmail.com"

yag = yagmail.SMTP(os.getenv("GMAIL_ACCOUNT"), oauth2_file="oauth.json")
yag.send(to=send_to_email, subject='Testing Yagmail', contents='Hurray, it worked!')
print("Email sent successfully")