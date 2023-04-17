from src.bond import Bond
from src.email_sender import EmailSender, EmailSenderResource
from src.file_service import FileService


if __name__ == "__main__":
  # generate report
  df = FileService.create_dataframe_from_bonds([Bond()])
  FileService.save_excel([("data", df)])

  # send report
  with EmailSenderResource(
      smtp_server="",
      port=1,
      sender_email="",
      password=""
  ) as es:
    emailSender: EmailSender = es
    emailSender.send_report_email()
