from pydantic import BaseModel


# ==========================
# User Schemas
# ==========================

class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ==========================
# Tree Schemas
# ==========================

class TreeCreate(BaseModel):
    species_name: str
    location: str
    health_status: str


class TreeUpdate(BaseModel):
    health_status: str