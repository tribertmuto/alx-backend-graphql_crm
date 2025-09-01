import logging
from celery import shared_task

@shared_task
def generatecrmreport():
    log_file = '/tmp/crmreportlog.txt'
    try:
        with open(log_file, 'a') as f:
            f.write('CRM report generated successfully.\n')
        return 'Report generated and logged.'
    except Exception as e:
        logging.error(f'Error generating CRM report: {e}')
        return f'Error: {e}'
