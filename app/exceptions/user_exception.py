from .base_exception import ServiceException, PermissionDenied, NotFound


class UserAlreadyExists(ServiceException):
    status_code = 400
    detail = 'User already exists'

class UsernameAlreadyTaken(UserAlreadyExists):
    detail = 'Username is already taken'

class EmailAlreadyRegistered(UserAlreadyExists):
    detail = 'Email is already registered'

class UserNotFound(NotFound):
    detail = 'User not found'

class PermissionDeniedUser(PermissionDenied):
    detail = 'Permission denied'

class CannotDemoteSelf(ServiceException):
    status_code = 400
    detail = 'Administrators cannot demote themselves'
