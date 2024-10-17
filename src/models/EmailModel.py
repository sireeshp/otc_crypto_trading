from typing import Union

from pydantic import BaseModel, EmailStr


class EmailModel(BaseModel):
    from_email: Union[EmailStr, None]
    to: EmailStr
    subject: str
    plain_text_content: str
    html_content: str
