from pydantic import BaseModel, validator
from exceptions import SmscApiError


class FormValidator(BaseModel):
    text: str

    @validator('text')
    def check_text_field(cls, v):
        if not v:
            raise SmscApiError('Text field cannot be empty')

        return v
