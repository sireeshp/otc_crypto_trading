from typing import Optional

from pydantic import BaseModel, EmailStr


class EmailModel(BaseModel):
    from_email: Optional[EmailStr]
    to: EmailStr
    subject: str
    plain_text_content: str
    html_content: str
    template_id: Optional[str]
