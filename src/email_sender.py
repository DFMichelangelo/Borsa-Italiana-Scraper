from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path
import smtplib
import ssl

class EmailSender:
  
  context = ssl.create_default_context()
  def __init__(self,
    smtp_server: str,
    port: int,
    sender_email:str,
    password:str) -> None:
    
    self.server = smtplib.SMTP(smtp_server,port)
    self.server.starttls(context=self.context) # Secure the connection
    self.server.login(sender_email, password)
    self.smtp_server=smtp_server
    self.sender_email=sender_email
    self.port=port
    self.password=password


  
  def send_report_email(self)-> None:
    excel_path = path.join("out", "output_scrapring.xlsx")
    # check that the output file exists
    if path.exists(excel_path):
      subject = "An email with attachment from Python"
      body = "This is an email with attachment sent from Python"
      receiver_email = "your@gmail.com"
      message = MIMEMultipart()
      message["From"] = self.sender_email
      message["To"] = receiver_email
      message["Subject"] = subject
      message["Bcc"] = receiver_email
      body = "This is an email with attachment sent from Python"
      message.attach(MIMEText(body, "plain"))

      part = MIMEBase('application', "octet-stream")
      part.set_payload(open(excel_path, "rb").read())
      # Encode file in ASCII characters to send by email    
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="report_bonds.xlsx"')
      message.attach(part)

      # Add attachment to message and convert message to string
      message.attach(part)
      text = message.as_string()
      self.server.sendmail(self.sender_email, receiver_email, text)

    else:
      raise FileNotFoundError(f'{excel_path} does not exist')

  def is_connected(self)->bool:
    try:
        status = self.server.noop()[0]
    except:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False
  
  def close_connection(self)->None:
    self.server.quit()



class EmailSenderResource:
  def __enter__(self,
    smtp_server: str,
    port: int,
    sender_email:str,
    password:str
    ):
    self.email_sender = EmailSender(
    smtp_server,
    port,
    sender_email,
    password
    )
    return self.email_sender

  def __exit__(self, exc_type, exc_value, traceback):
    self.email_sender.close_connection()