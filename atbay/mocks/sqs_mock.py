import json
import logging
from collections import deque
from pathlib import Path

BASE_PATH = str(Path(Path(__file__).parent.parent.absolute()))
logging.info(BASE_PATH)


class SqsMock:
    def __init__(self):
        """
        Mock for AWS SQS service
        """
        self._sqs_path = f'{BASE_PATH}/local_sqs.json'
        self._queue = deque()
        with open(self._sqs_path, 'a+') as f:
            f.seek(0)
            if f.readlines():
                f.seek(0)
                lst = json.load(f)
                [self._queue.append(val) for val in lst]

    def put(self, obj):
        self.load()
        self._queue.append(obj)
        self.save()

    def get(self):
        self.load()
        if len(self._queue):
            item = self._queue.pop()
            self.save()
            return item
        else:  # queue is empty
            return None

    def load(self):
        with open(self._sqs_path, 'r') as f:
            try:
                self._queue = json.load(f)
            except ValueError:
                self._queue = []

    def save(self):
        with open(self._sqs_path, 'w') as f:
            json.dump(list(self._queue), f)


# create global SQS mock
sqs_mock = SqsMock()
