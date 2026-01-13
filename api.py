import requests
import logging
from algorithm import algothihm
from models import RotateCaptchaResponse

class ApiClient:

    def __init__(self) -> None:
        pass

    def rotate(self, outer_b64: str, inner_b64: str) -> RotateCaptchaResponse:
        """Slide the slider to rotate the images"""
        data = {
            "innerImageB64": inner_b64,
            "outerImageB64": outer_b64,
        }        
        
        resp = algothihm(data).rotate()
        return RotateCaptchaResponse(angle=round(resp))
    
