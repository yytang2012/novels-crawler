import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailAPIs:
    doms = {
        'gmail.com': ['smtp.gmail.com', 587],
    }

    def __init__(self, email_address, password):
        self.email_address = email_address
        my_dom = email_address.split('@')[1].strip()
        host, port = self.doms[my_dom]
        self.server = smtplib.SMTP(host=host, port=port)
        self.server.starttls()
        self.server.login(email_address, password)
        print(host, port)

    def send_message_to_one(self, destination_address, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = destination_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        self.server.send_message(msg)
        del msg


if __name__ == '__main__':
    MY_EMAIL = 'xxxx@gmail.com'
    PASSWORD = 'password'
    try:
        email = EmailAPIs(MY_EMAIL, PASSWORD)
        body = 'This is the body'
        subject = 'This is subject'
        destination_address = 'kissingers800@gmail.com'
        email.send_message_to_one(destination_address, subject, body)
        print('message has been sent successfully')
    except Exception as e:
        print("Error happened when trying to send the message")
