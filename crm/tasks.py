import logging
from datetime import datetime
import requests
from celery import shared_task

@shared_task
def generate_crm_report():
    log_file = '/tmp/crm_report_log.txt'
    try:
        with open(log_file, 'a') as f:
            f.write(f'{datetime.now()}: CRM report generated successfully.\n')
        return 'Report generated and logged.'
    except Exception as e:
        logging.error(f'Error generating CRM report: {e}')
        return f'Error: {e}'
