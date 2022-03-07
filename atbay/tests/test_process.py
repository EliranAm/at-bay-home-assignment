import json
import logging
import unittest
import requests
from atbay.src.process import incoming_records
from atbay.src.status_code import StatusCode


class TestProcess(unittest.TestCase):
    STATUS_URL = 'http://127.0.0.1:3000'
    INGEST_URL = 'http://127.0.0.1:4000'

    @staticmethod
    def _build_record(scan_id, url):
        return {
            "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
            "receiptHandle": "MessageReceiptHandle",
            "body": {'scan_id': scan_id, 'url': url},
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1523232000000",
                "SenderId": "123456789012",
                "ApproximateFirstReceiveTimestamp": "1523232000001"
            },
            "messageAttributes": {},
            "md5OfBody": "{{{md5_of_body}}}",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
            "awsRegion": "us-east-1"
        }

    def test_ingest_valid_url(self):
        session = requests.Session()
        result = session.get(f'{self.INGEST_URL}/ingest/scan/test123', timeout=60)
        self.assertEqual(result.status_code, 200)

    def test_ingest_valid_bulk(self):
        data = [{'url': 'mydomain'}, {'url': 'somedomain'}]
        session = requests.Session()
        result = session.post(f'{self.INGEST_URL}/ingest/bulk', json=data, timeout=60)
        ret_data = json.loads(result.text)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(ret_data), len(data))

    def test_ingest_empty_data_bulk(self):
        data = []
        session = requests.Session()
        result = session.post(f'{self.INGEST_URL}/ingest/bulk', json=data, timeout=60)
        ret_data = json.loads(result.text)
        self.assertEqual(result.status_code, 500)
        self.assertEqual(len(ret_data), 0)

    def test_ingest_wrong_type_bulk(self):
        data = 123
        session = requests.Session()
        result = session.post(f'{self.INGEST_URL}/ingest/bulk', json=data, timeout=60)
        ret_data = json.loads(result.text)
        self.assertEqual(result.status_code, 500)
        self.assertEqual(len(ret_data), 0)

    def test_ingest_wrong_values_bulk(self):
        data = {'url': 12345}
        session = requests.Session()
        result = session.post(f'{self.INGEST_URL}/ingest/bulk', json=data, timeout=60)
        ret_data = json.loads(result.text)
        self.assertEqual(result.status_code, 500)
        self.assertEqual(len(ret_data), 0)

    def test_ingest_wrong_keys_bulk(self):
        data = {'urls': 'lalala'}
        session = requests.Session()
        result = session.post(f'{self.INGEST_URL}/ingest/bulk', json=data, timeout=60)
        self.assertEqual(result.status_code, 500)
        ret_data = json.loads(result.text)
        self.assertEqual(len(ret_data), 0)

    def test_status_valid_id(self):
        session = requests.Session()
        ingest_res = session.get(f'{self.INGEST_URL}/ingest/scan/my_domain', timeout=60)
        self.assertEqual(ingest_res.status_code, 200)
        result = session.get(f'{self.STATUS_URL}/status/{ingest_res.text}', timeout=60)
        self.assertEqual(result.status_code, 200)
        self.assertNotEqual(result.text, StatusCode.NOT_FOUND.value)

    def test_status_invalid_id(self):
        session = requests.Session()
        result = session.get(f'{self.STATUS_URL}/status/zzz', timeout=60)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, StatusCode.NOT_FOUND.value)

    def test_process_valid_record(self):
        domain_name = 'first_domain'
        session = requests.Session()
        ingest_res = session.get(f'{self.INGEST_URL}/ingest/scan/{domain_name}', timeout=60)
        self.assertEqual(ingest_res.status_code, 200)
        rec = self._build_record(ingest_res.text, domain_name)
        event = {'Records': [rec]}
        incoming_records(event, {})
        status_result = session.get(f'{self.STATUS_URL}/status/{ingest_res.text}', timeout=60)
        self.assertEqual(status_result.status_code, 200)
        self.assertIn(status_result.text, [StatusCode.COMPLETE.value, StatusCode.ERROR.value])

    def test_process_valid_few_records(self):
        records = []
        domain_name = 'my_domains_'
        session = requests.Session()
        ingest_res = session.get(f'{self.INGEST_URL}/ingest/scan/{domain_name}1', timeout=60)
        records.append(self._build_record(ingest_res.text, domain_name))
        ingest_res = session.get(f'{self.INGEST_URL}/ingest/scan/{domain_name}2', timeout=60)
        records.append(self._build_record(ingest_res.text, domain_name))
        event = {'Records': records}
        incoming_records(event, {})
        status_result = session.get(f'{self.STATUS_URL}/status/{ingest_res.text}', timeout=60)
        self.assertEqual(status_result.status_code, 200)
        self.assertIn(status_result.text, [StatusCode.COMPLETE.value, StatusCode.ERROR.value])

    def test_process_invalid_record(self):
        domain_name = 'first_domain'
        fake_id = 'not-exist-id'
        session = requests.Session()
        rec = self._build_record(fake_id, domain_name)
        event = {'Records': [rec]}
        logging.warning('Expected error in incoming_records: Failed to find scan id in db')
        incoming_records(event, {})
        status_result = session.get(f'{self.STATUS_URL}/status/{fake_id}', timeout=60)
        self.assertEqual(status_result.status_code, 200)
        self.assertEqual(status_result.text, StatusCode.NOT_FOUND.value)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
