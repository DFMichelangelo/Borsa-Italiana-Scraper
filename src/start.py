from src.email_sender import EmailSenderResource
from .scraper import Scraper
from .file_service import FileService
import os


def start():
  print("--- Start ---")
  scraper = Scraper(2)
  bonds = scraper.get_data()
  print("--- Finished scraping, saving file  ---")
  df_bonds = FileService.create_dataframe_from_bonds(bonds)
  data_to_excel = ("all_bonds", df_bonds)
  FileService.save_excel([data_to_excel])
  # send report
  should_send_email = os.environ("SHOULD_SEND_EMAIL")
  if should_send_email is not None and bool(should_send_email):
    with EmailSenderResource(
        smtp_server=os.environ("SMTP_SERVER"),
        port=int(os.environ("PORT")),
        sender_email=os.environ("EMAIL"),
        password=os.environ("PASSWORD"),
    ) as email_sender:
      email_sender.send_report_email(receivers=os.environ("RECEIVERS"))
