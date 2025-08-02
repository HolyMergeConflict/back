import abc

from app.logger import setup_logger

logger = setup_logger(__name__)

class ServiceException(Exception):
    status_code: int = 400
    detail: str = 'Service exception occurred'

    def __init__(self, detail: str = None, status_code: int = None, log: bool = True):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code

        if log:
            logger.warning(f'[{self.__class__.__name__}] {self.detail} (HTTP {self.status_code})')
        super().__init__(self.detail)

class MissingRequiredParameters(ServiceException):
    default_detail = 'Missing required parameters'

    def __init__(self, detail: str = None):
        super().__init__(detail or self.default_detail, status_code=400)

class PermissionDenied(ServiceException, abc.ABC):
    status_code = 403

class NotFound(ServiceException, abc.ABC):
    status_code = 404