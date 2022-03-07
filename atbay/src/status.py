from flask import Flask
from atbay.mocks.dynamo_mock import dynamo_mock
from atbay.src.status_code import StatusCode


app = Flask(__name__)


@app.route('/')
def home():
    return 'ping'


@app.route('/status/<scan_id>')
def ingest_scan(scan_id):
    """
    Get the status of ingested scan
    :param scan_id: scan id (uuid)
    :return: Scan status
    """
    value = dynamo_mock.get_item(scan_id)
    if value and 'status' in value:
        return value['status']
    else:  # scan id not found
        return StatusCode.NOT_FOUND.value


if __name__ == '__main__':
    app.run(port=3000)
