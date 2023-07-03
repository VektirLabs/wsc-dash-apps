import smtplib as smtp

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

address_book = ['wscrigadvisor@conocophillips.com']
msg = MIMEMultipart()
sender = 'wscrigadvisor@conocophillips.com'
subject = "My subject"
body = "This is my email body"

msg['From'] = sender
msg['To'] = ','.join(address_book)
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))
text=msg.as_string()
#print text
# Send the message via our SMTP server
s = smtp.SMTP('wscrigadvicor@conocophillips.com')
s.sendmail(sender,address_book, text)
s.quit()
