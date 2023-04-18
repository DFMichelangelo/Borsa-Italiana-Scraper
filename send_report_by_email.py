from src.bond import Bond
from src.email_sender import EmailSender, EmailSenderResource
from src.file_service import FileService
from src.scraper import Scraper

if __name__ == "__main__":
  # generate report
  scraper = Scraper()
  bonds = scraper.get_data()
  df = FileService.create_dataframe_from_bonds(bonds)
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
