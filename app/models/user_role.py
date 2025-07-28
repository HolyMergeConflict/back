from enum import Enum


class UserRoleEnum(str, Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'
    MODERATOR = 'moderator'
    ADMIN = 'admin'