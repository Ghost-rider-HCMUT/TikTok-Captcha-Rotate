import time
from selenium.webdriver import ActionChains, Chrome
from selenium.webdriver.common.by import By
import captcha_selectors as selectors
from geometry import compute_rotate_slide_distance
from captchatype import CaptchaType
from api import ApiClient
from solver import Solver


class SeleniumSolver(Solver):

    client: ApiClient
    chromedriver: Chrome

    def __init__(self, chromedriver: Chrome) -> None:
        self.chromedriver = chromedriver
        self.client = ApiClient()
        self.version = None

    def fetch_image_from_element(self, element):
        image = self.chromedriver.find_elements(By.CSS_SELECTOR, element)
        script = """
            var img = arguments[0];
            var canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png').substring(22);
        """
        for i, img in enumerate(image):
            try:
                img_base64 = self.chromedriver.execute_script(script, img)
                return img_base64
            except Exception:
                return None
    
    def captcha_is_present(self, timeout: int = 15) -> bool:
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self._any_selector_in_list_present([
                selectors.Wrappers.V1,
                selectors.Wrappers.V2
            ]):
                return True
            time.sleep(0.5)
        return False
    

    def identify_captcha(self) -> CaptchaType:
        # Kiểm tra SELECT_OBJECTS trước (dựa vào alt text)
        if self._is_select_objects_captcha():
            self.version = 2
            return CaptchaType.SELECT_OBJECTS
        # Kiểm tra V1 với nhiều điều kiện
        if self._is_rotate_captcha_v1():
            self.version = 1
            return CaptchaType.ROTATE_V1
        # Còn lại trả về OTHER để báo hiệu không nhận ra
        return CaptchaType.OTHER

    def solve_rotate(self) -> None:
        if not self._any_selector_in_list_present([selectors.RotateV1.INNER]):
            return
        
        outer = self.fetch_image_from_element(selectors.RotateV1.OUTER)
        inner = self.fetch_image_from_element(selectors.RotateV1.INNER)
        
        solution = self.client.rotate(outer, inner)
        slide_bar_width = self._get_element_width(selectors.RotateV1.SLIDE_BAR)
        slider_button_width = self._get_element_width(selectors.RotateV1.SLIDER_DRAG_BUTTON)
        distance = compute_rotate_slide_distance(solution.angle, slide_bar_width, slider_button_width)
        self._drag_element_horizontal(selectors.RotateV1.SLIDER_DRAG_BUTTON, distance, None, 1)

    def _get_element_width(self, selector: str) -> int:
        e = self.chromedriver.find_element(By.CSS_SELECTOR, selector)
        return e.size['width']

    def _drag_element_horizontal(self, css_selector: str, x: int, frame_selector: str | None = None, version: int = 2) -> None:
        try:
            e = self.chromedriver.find_element(By.CSS_SELECTOR, css_selector)
            if version == 1:
                slider_captcha_location = self.chromedriver.find_element(By.CSS_SELECTOR, css_selector)
                actions = ActionChains(self.chromedriver, duration=550)
                actions.click_and_hold(slider_captcha_location)
                actions.move_by_offset(x, 0)
                for i in range(5):
                    actions.move_by_offset(1, 0)
                for j in range(5):
                    actions.move_by_offset(-1,0)
                actions.release().perform()
        finally:
            self.chromedriver.switch_to.default_content()

    def _any_selector_in_list_present(self, selectors: list[str]) -> bool:
        for selector in selectors:
            for ele in self.chromedriver.find_elements(By.CSS_SELECTOR, selector):
                if ele.is_displayed():
                    return True
        return False
    
    def _is_rotate_captcha_v1(self) -> bool:
        """Kiểm tra xem có phải là captcha xoay tròn V1 không"""
        # 1. Kiểm tra container chính
        if not self._any_selector_in_list_present([selectors.Wrappers.V1]):
            return False
            
        # 2. Kiểm tra có ảnh với clip-path: circle
        circular_images = self.chromedriver.find_elements(
            By.CSS_SELECTOR, 
            '#captcha-verify-container-main-page img[style*="clip-path: circle"]'
        )
        if len(circular_images) < 2:  # Cần ít nhất 2 ảnh (outer + inner)
            return False
            
        # 3. Kiểm tra có ảnh absolute (mảnh ghép)
        if not self._any_selector_in_list_present([selectors.RotateV1.INNER]):
            return False
            
        # 4. Kiểm tra có thanh trượt tròn
        if not self._any_selector_in_list_present([selectors.RotateV1.SLIDE_BAR]):
            return False
            
        return True
    
    def _is_select_objects_captcha(self) -> bool:
        """Kiểm tra xem có phải là captcha chọn objects không (dựa vào alt text)"""
        # 1. Kiểm tra container chính
        if not self._any_selector_in_list_present([selectors.Wrappers.V2]):
            return False
            
        # 2. Kiểm tra có ảnh với alt="Verify that you're not a robot"
        verify_images = self.chromedriver.find_elements(
            By.CSS_SELECTOR,
            'img[alt="Verify that you\'re not a robot"]'
        )
        if len(verify_images) == 0:
            return False
            
        # 3. Kiểm tra có text instruction về "Select 2 objects"
        instruction_elements = self.chromedriver.find_elements(
            By.XPATH,
            '//span[contains(text(), "Select 2 objects")]'
        )
        if len(instruction_elements) == 0:
            return False
            
        # 4. Đảm bảo không phải rotate captcha (không có clip-path: circle)
        circular_images = self.chromedriver.find_elements(
            By.CSS_SELECTOR,
            'img[style*="clip-path: circle"]'
        )
        if len(circular_images) > 0:  # Nếu có clip-path circle thì là rotate captcha
            return False
            
        return True
    
    def _is_rotate_captcha_v2(self) -> bool:
        """Kiểm tra xem có phải là captcha xoay tròn V2 không"""
        # Tương tự như V1 nhưng với selectors V2
        if not self._any_selector_in_list_present([selectors.Wrappers.V2]):
            return False
            
        circular_images = self.chromedriver.find_elements(
            By.CSS_SELECTOR, 
            '.captcha-verify-container img[style*="clip-path: circle"]'
        )
        if len(circular_images) < 2:
            return False
            
        if not self._any_selector_in_list_present([selectors.RotateV2.INNER]):
            return False
            
        return True
