from enum import Enum


class TaskStatusEnum(str, Enum):
    PENDING = 'pending',
    APPROVED = 'approved',
    REJECTED = 'rejected',