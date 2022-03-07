import logging
import random
from datetime import datetime, timezone
from time import sleep
from atbay.mocks.dynamo_mock import dynamo_mock
from atbay.mocks.sqs_mock import sqs_mock
from atbay.src.status_code import StatusCode


def incoming_records(event, context):
    """
    This function triggered when new records arrived to SQS
    Its connect as lambda entry with event trigger.
    :param event: records and meta data
    :param context: context data
    """
    for record in event['Records']:
        data = record['body']  # In real SQS: record = json.loads(record['body'])
        status = _handle_scan_record(data)
        logging.info(f'Process scan id {data.get("scan_id")} complete with status {status}')


def _process_scan(url):
    # scanning...
    logging.info(f'Start scanning {url} domain...')
    sleep(3)
    logging.info(f'End scanning {url} domain...')

    # return complete status unless res is equal to 5, else return error status
    res = random.randint(0, 10)
    return StatusCode.COMPLETE.value if res != 5 else StatusCode.ERROR.value


def _handle_scan_record(sqs_rec):
    scan_id = sqs_rec.get('scan_id', '')
    url = sqs_rec.get('url', '')

    # update status to running
    db_value = {
        'status': StatusCode.RUNNING.value,
        'timestamp': int(datetime.now(tz=timezone.utc).timestamp())
    }
    res = dynamo_mock.update_item(scan_id, db_value)
    if res:
        # scan the domain
        status = _process_scan(url)
        # update status to complete or error
        db_value = {
            'status': status,
            'timestamp': int(datetime.now(tz=timezone.utc).timestamp())
        }
        dynamo_mock.update_item(scan_id, db_value)
        logging.info('Finish scan and update successfully.')
    else:  # update db item failed
        status = StatusCode.NOT_FOUND.value
        logging.error(f'Failed to find scan id in db.')

    return status

