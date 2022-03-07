import uuid
from flask import Flask, request, make_response
from datetime import datetime, timezone
from atbay.mocks.dynamo_mock import dynamo_mock
from atbay.mocks.sqs_mock import sqs_mock
from atbay.src.status_code import StatusCode


app = Flask(__name__)


@app.route('/')
def home():
    return 'ping'


@app.route('/ingest/scan/<url>')
def ingest_scan(url):
    """
    Received scan request and add it to queue for dispatching
    :param url: the domain to scan
    :return: scan id for monitor progress
    """
    return _handle_scan(url)


def _handle_scan(url):
    # 1. Validate URL
    # 2. Generate scan id
    # 3. Insert scan to queue
    # 4. Insert scan status to dynamo

    ret_val = None

    if url:
        scan_id = str(uuid.uuid4())
        db_value = {
            'status': StatusCode.ACCEPTED.value,
            'timestamp': int(datetime.now(tz=timezone.utc).timestamp())
        }
        res = dynamo_mock.put_item(scan_id, db_value)
        if res:
            sqs_value = {
                'scan_id': scan_id,
                'url': url
            }
            sqs_mock.put(sqs_value)
            # set scan id as return value
            ret_val = scan_id

    return ret_val


@app.route('/ingest/bulk', methods=['POST'])
def ingest_scans_bulk():
    """
    Received batch of scan requests and add them to queue for dispatching
    :param: json payload with all urls. example: {'url': 'example_domain'}
    :return: scan id for monitor progress
    """
    status_code = 500
    ret_values = {}
    bulk = request.get_json()
    if isinstance(bulk, list):
        for job in bulk:
            url = job.get('url', '')
            scan_id = _handle_scan(url)
            ret_values[url] = scan_id
            status_code = 200

    return make_response(ret_values, status_code)


if __name__ == '__main__':
    app.run(port=4000)
