from src.email_sender import EmailSenderResource
from src.file_service import FileService


def send_email_with_report()->None:

  #generate report
  df = FileService.create_dataframe_from_bonds();
  FileService.save_excel([("data",df)])
  
  #send report
  with EmailSenderResource() as emailSender:
    emailSender.send_report_email()



if __name__=="__main__":
    send_email_with_report()