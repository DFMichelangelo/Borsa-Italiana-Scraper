from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path
import smtplib
from contextlib import contextmanager


class EmailSender:

  def __init__(self,
               smtp_server: str,
               port: int,
               sender_email: str,
               password: str) -> None:
    self.server = smtplib.SMTP_SSL(smtp_server, port)
    self.server.login(sender_email, password)
    self.smtp_server = smtp_server
    self.sender_email = sender_email
    self.port = port
    self.password = password

  def send_report_email(self, receivers) -> None:
    excel_path = path.join("out", "scraped.xlsx")
    # check that the output file exists
    if path.exists(excel_path):
      subject = "An email with attachment from Python"
      body = "This is an email with attachment sent from Python"
      message = MIMEMultipart()
      message["From"] = self.sender_email
      message["To"] = receivers
      message["Subject"] = subject
      body = "This is an email with attachment sent from Python"
      message.attach(MIMEText(body, "plain"))

      part = MIMEBase('application', "octet-stream")
      part.set_payload(open(excel_path, "rb").read())
      # Encode file in ASCII characters to send by email
      encoders.encode_base64(part)
      part.add_header('Content-Disposition',
                      'attachment; filename="report_bonds.xlsx"')
      message.attach(part)

      # Add attachment to message and convert message to string
      message.attach(part)
      text = message.as_string()
      self.server.sendmail(self.sender_email, receivers, text)

    else:
      raise FileNotFoundError(f'{excel_path} does not exist')

  def is_connected(self) -> bool:
    try:
      status = self.server.noop()[0]
    except BaseException:  # smtplib.SMTPServerDisconnected
      status = -1
    return True if status == 250 else False

  def close_connection(self) -> None:
    self.server.quit()


@contextmanager
def EmailSenderResource(
    smtp_server: str,
    port: int,
    sender_email: str,
    password: str
):
  email_sender: EmailSender

  try:
    email_sender = EmailSender(
        smtp_server,
        port,
        sender_email,
        password
    )
    yield email_sender
  finally:
    email_sender.close_connection()
