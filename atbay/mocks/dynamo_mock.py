import json
import logging
from pathlib import Path

BASE_PATH = str(Path(Path(__file__).parent.parent.absolute()))
logging.info(BASE_PATH)


class DynamoMock:
    def __init__(self):
        """
        Mock for AWS DynamoDB service
        Note: Remove completed tasks from DB will define using TTL in Dynamo DB configuration base on timestamp attribute
        """
        self._db_path = f'{BASE_PATH}/local_dynamo_db.json'
        self._db = {}
        with open(self._db_path, 'a+') as f:
            f.seek(0)
            if f.readlines():
                f.seek(0)
                self._db = json.load(f)

    def put_item(self, key, val):
        self.load()
        if key not in self._db:
            self._db[key] = val
            self.save()
            return True
        else:
            return False

    def get_item(self, key):
        self.load()
        return self._db.get(key)

    def update_item(self, key, val):
        self.load()
        if key in self._db:
            self._db[key] = val
            self.save()
            return True
        else:
            return False

    def remove_item(self, key):
        self.load()
        if key in self._db:
            self._db.pop(key)
            self.save()
            return True
        else:
            return False

    def load(self):
        with open(self._db_path, 'r') as f:
            try:
                self._db = json.load(f)
            except ValueError:
                self._db = {}

    def save(self):
        with open(self._db_path, 'w') as f:
            json.dump(self._db, f)


# create global dynamo DB mock
dynamo_mock = DynamoMock()
