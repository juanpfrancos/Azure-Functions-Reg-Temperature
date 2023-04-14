
import os
import smtplib
import logging
import azure.functions as func
import pandas as pd
from datetime import datetime
from requests import get
from io import BytesIO
from xlsxwriter.utility import xl_range
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def main(mytimer: func.TimerRequest) -> None:
    try:
        data = get_data()
        xlsx_file = xlsx_base_function(data)
        send_email(xlsx_file)
    except Exception as e:
        logging.error(str(e))



def get_data():
    try:
        resp = get(os.environ["ENDPOINT_GET"])
        data = resp.json()
        items = data.get('items')
        return items
    except Exception as e:
        logging.error(f"Error getting data: {str(e)}")
        raise ValueError("Error getting data")
        
def xlsx_base_function(data):
    try:
        mem = BytesIO()
        with pd.ExcelWriter(mem) as writer:
            sheet_name ="Data"
            df = pd.DataFrame.from_dict(data, orient='columns')
            total_columns = len(df.columns)
            total_rows = len(df.index)
            cell_range = xl_range(0, 0, total_rows, total_columns-1)                
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            workbook  = writer.book
            worksheet = writer.sheets[sheet_name]
            col_format = workbook.add_format({'border':1, 'border_color':'black'})
            worksheet.set_column(0, total_columns-1, 20)
            worksheet.conditional_format(cell_range, {'type':'text','criteria':'not containing','value':'BCGJhTPjAxLQEk3gwt6FzvRqX','format':col_format})
        mem.seek(0)
        file_ = mem.read()
        return file_
    except Exception as e:
        logging.error(f"Error generating xlsx: {str(e)}")
        raise ValueError("Error generating xlsx")               


def send_email(file_):
    try:
        now = datetime.now().isoformat()
        sender_email = os.environ["SENDER_EMAIL"]
        receiver_email = os.environ["REC_EMAIL"]
        password_app = os.environ["PWD_APP"]
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"Informe horario {now}"
        body = f"Hola, adjunto el archivo de excel {now}"
        message.attach(MIMEText(body, "plain"))
        attach = MIMEApplication(file_, _subtype = "xlsx")
        attach.add_header("Content-Disposition", "attachment", filename = f"archivo{now.replace(':','')}.xlsx")
        message.attach(attach)
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, password_app)
            smtp.send_message(message)
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        raise ValueError("Error sending email") 