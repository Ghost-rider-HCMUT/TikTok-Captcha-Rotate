"""Abstract base class for Tiktok Captcha Solvers"""

from abc import ABC, abstractmethod
from captchatype import CaptchaType

class Solver(ABC):

    @abstractmethod
    def captcha_is_present(self, timeout: int = 15) -> bool:
        pass

    @abstractmethod
    def identify_captcha(self) -> CaptchaType:
        pass

    @abstractmethod
    def solve_rotate(self) -> None:
        pass