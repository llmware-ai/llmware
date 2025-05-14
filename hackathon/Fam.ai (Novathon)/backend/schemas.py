from typing import Union, List

from pydantic import BaseModel


class AccountData(BaseModel):
    address: str


class ProfileUID(BaseModel):
    prfid: str


class ProfileData(BaseModel):
    address: Union[str, None] = None
    prfid: Union[str, None] = None
    name: str
    dob: str
    gender: str
    blood: str


class DocData(BaseModel):
    filename: Union[str, None] = None
    inferences: str

    address: Union[str, None] = None
    prfid: Union[str, None] = None


class ChatData(BaseModel):
    prfid: str
    prompt: str
    history: List


