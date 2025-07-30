from enum import Enum


class TaskStatus(str, Enum):
    pending = 'pending',
    approved = 'approved',
    rejected = 'rejected',