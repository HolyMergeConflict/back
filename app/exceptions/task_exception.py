from app.exceptions.base_exception import ServiceException, PermissionDenied, NotFound


class PermissionDeniedTask(PermissionDenied):
    detail = 'Insufficient permission to moderate task'

class TaskNotFound(NotFound):
    detail = 'Task not found'

class TaskNotPendingModeration(ServiceException):
    status_code = 400
    detail = 'task is not pending moderation'
