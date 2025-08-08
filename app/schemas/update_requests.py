from pydantic import BaseModel
from app.enums.user_role import UserRoleEnum

class UpdateRoleRequest(BaseModel):
    role: UserRoleEnum