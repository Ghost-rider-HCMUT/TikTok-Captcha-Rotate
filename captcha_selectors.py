class Wrappers:
    V1 = "#captcha-verify-container-main-page"
    V2 = ".captcha-verify-container"

class RotateV1:
    INNER = "#captcha-verify-container-main-page img.cap-absolute"
    OUTER = "#captcha-verify-container-main-page img:first-child"
    SLIDE_BAR = "#captcha-verify-container-main-page .cap-rounded-full"
    SLIDER_DRAG_BUTTON = ".secsdk-captcha-drag-icon"
    UNIQUE_IDENTIFIER = "#captcha-verify-container-main-page img.cap-absolute"

class RotateV2:
    INNER = ".captcha-verify-container > div > div > div > img.cap-absolute"
    OUTER = ".captcha-verify-container > div > div > div > img:first-child"
    SLIDE_BAR = ".captcha-verify-container > div > div > div.cap-w-full > div.cap-rounded-full"
    SLIDER_DRAG_BUTTON = ".secsdk-captcha-drag-icon"
    UNIQUE_IDENTIFIER = ".captcha-verify-container > div > div > div > img.cap-absolute"