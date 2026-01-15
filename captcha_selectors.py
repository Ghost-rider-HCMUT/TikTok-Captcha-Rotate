class   Wrappers:
    V1 = "#captcha_container"
    V2 = ".captcha-verify-container"

class RotateV1:
    INNER = "#captcha-verify-container-main-page img.cap-absolute"
    OUTER = "#captcha-verify-container-main-page img:first-child"
    SLIDE_BAR = "#captcha-verify-container-main-page .cap-rounded-full"
    SLIDER_DRAG_BUTTON = ".secsdk-captcha-drag-icon"
    UNIQUE_IDENTIFIER = "#captcha-verify-container-main-page img.cap-absolute"
    # Selector mới để nhận biết captcha tròn
    CIRCULAR_IMAGES = '#captcha-verify-container-main-page img[style*="clip-path: circle"]'
    CAPTCHA_CONTAINER = '.cap-flex.cap-flex-col.cap-justify-center.cap-items-center'

class SelectObjects:
    # Main captcha image với alt="Verify that you're not a robot"
    MAIN_IMAGE = 'img[alt="Verify that you\'re not a robot"]'
    # Container chính chứa captcha
    CONTAINER = '.captcha-verify-container'
    # Confirm button
    CONFIRM_BUTTON = 'button:has-text("Confirm")'
    # Text instruction về selecting objects
    INSTRUCTION_TEXT = 'span:has-text("Select 2 objects")'  
    # Unique identifier cho loại này
    UNIQUE_IDENTIFIER = 'img[alt="Verify that you\'re not a robot"]'