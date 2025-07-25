from enum import Enum


class UserRole(str, Enum):
    student = 'student'
    teacher = 'teacher'
    moderator = 'moderator'
    admin = 'admin'