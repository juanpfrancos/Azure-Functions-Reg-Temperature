import logging, os
import azure.functions as func
from requests import get,post
from datetime import datetime

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')    
    try:
        endpoint = os.environ['ENDPOINT_POST']
        body = req.get_json()
        now = datetime.now().isoformat()
        body.update({'reg_date':now})
        headers = { 'Content-Type': "application/json" }
        response = post(url=endpoint, json=body, headers=headers)
        if response.status_code == 200:
            return func.HttpResponse(
                    "Data successfully inserted",
                    status_code=200
            )
        else:
            ip = get(url='https://api.ipify.org')
            logging.info(f'IP: {ip.text}')
            return func.HttpResponse(
                    response.text,
                    status_code=400
            )
            
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(
                f"Error: {str(e)}",
                status_code=400
        )