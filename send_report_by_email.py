from src.email_sender import EmailSenderResource
from src.file_service import FileService


if __name__ == "__main__":
  # generate report
  df = FileService.create_dataframe_from_bonds()
  FileService.save_excel([("data", df)])

  # send report
  with EmailSenderResource() as emailSender:
    emailSender.send_report_email()
