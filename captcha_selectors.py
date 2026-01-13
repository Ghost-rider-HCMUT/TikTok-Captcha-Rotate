class Wrappers:
    V1 = ".captcha-disable-scroll"
    V2 = ".captcha-verify-container"

class RotateV1:
    INNER = "[data-testid=whirl-inner-img]"
    OUTER = "[data-testid=whirl-outer-img]"
    SLIDE_BAR = ".captcha_verify_slide--slidebar"
    SLIDER_DRAG_BUTTON = ".secsdk-captcha-drag-icon"
    UNIQUE_IDENTIFIER = ".captcha-disable-scroll [data-testid=whirl-inner-img]"

class RotateV2:
    INNER = ".captcha-verify-container > div > div > div > img.cap-absolute"
    OUTER = ".captcha-verify-container > div > div > div > img:first-child"
    SLIDE_BAR = ".captcha-verify-container > div > div > div.cap-w-full > div.cap-rounded-full"
    SLIDER_DRAG_BUTTON = ".secsdk-captcha-drag-icon"
    UNIQUE_IDENTIFIER = ".captcha-verify-container > div > div > div > img.cap-absolute"