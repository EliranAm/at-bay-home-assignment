from enum import Enum


class StatusCode(Enum):
    ACCEPTED = 'Accepted'
    RUNNING = 'Running'
    ERROR = 'error'
    COMPLETE = 'Complete'
    NOT_FOUND = 'Not Found'
