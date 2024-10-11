from pydantic import BaseModel, EmailStr


class EmailMessageInfo(BaseModel):
    number: int
    email: EmailStr
    subject: str


class SendEmailStatus(BaseModel):
    total: int
    messages: list[EmailMessageInfo]
