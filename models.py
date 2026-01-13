from pydantic import BaseModel


class RotateCaptchaResponse(BaseModel):
    angle: int
