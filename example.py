import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import captcha_selectors as selectors
from seleniumsolver import SeleniumSolver
from captchatype import CaptchaType

def human_type(element, text, min_delay=0.05, max_delay=0.2):
    """Gõ text như người thật với delay ngẫu nhiên giữa các ký tự"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

def example(email, password):
    # Setup Option

    chrome_options = Options()
    # chrome_options.binary_location = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
    chrome_options.binary_location = r"C:/Program Files/CocCoc/Browser/Application/browser.exe"
    chrome_options.add_argument("--window-size=1200,960")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    prefs = {
    "credentials_enable_service": False,  # Tắt dịch vụ lưu thông tin đăng nhập
    "profile.password_manager_enabled": False # Tắt trình quản lý mật khẩu hoàn toàn
}
    chrome_options.add_experimental_option("prefs", prefs)


    # Khởi tạo Driver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    except Exception as e:
        print(f"Lỗi khởi tạo Driver: {e}")
        return

    wait = WebDriverWait(driver, 10)

    print("--- Bắt đầu Login ---")
    
    driver.get("https://www.tiktok.com/login/phone-or-email/email")

    # Nhập Email
    print("Nhập Email...")
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    email_input.click()
    email_input.clear()
    human_type(email_input, email)
    time.sleep(1)

    # Nhập Password
    print("Nhập Password...")
    pass_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    human_type(pass_input, password)
    time.sleep(1)

    # Click Login
    print("Click Login...")
    login_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_btn.click()
    time.sleep(2)

    # Xử lý Captcha
    print("Đang kiểm tra Captcha...")
    for i in range(5):
        try:
            captcha_check = driver.find_element(By.ID, "captcha-verify-container-main-page")
            
            if captcha_check and captcha_check.is_displayed():
                print("Captcha xuất hiện, đang xử lý...")
                try:
                    solver = SeleniumSolver(driver)
                    print("Solver created")
                except Exception as e:
                    print(f"❌ Error creating solver: {e}")
                    import traceback
                    traceback.print_exc()
                
                captcha_type = CaptchaType.OTHER 
              
                try:
                    if captcha_type == CaptchaType.OTHER:
                        if driver.find_element(By.XPATH, "//span[contains(text(), 'Select 2 objects')]"):
                            captcha_type = CaptchaType.SELECT_OBJECTS
                            print("Captcha loại SELECT_OBJECTS.")
                        elif captcha_check.find_element(By.XPATH, "//img[contains(@class, 'cap-absolute')]"):
                            captcha_type = CaptchaType.ROTATE_V1
                            print("Captcha loại ROTATE_V1.")
                except:
                    pass
                    
                if captcha_type == CaptchaType.ROTATE_V1:
                    print("Đang giải captcha RotateV1...")
                    solver.solve_rotate()
                    time.sleep(2)
                    break
                elif captcha_type == CaptchaType.SELECT_OBJECTS:
                    print("Đang giải captcha SELECT_OBJECTS...")    
                    time.sleep(2)
                    driver.quit()
                    return
                elif captcha_type == CaptchaType.OTHER:
                    print("Loại Captcha không được hỗ trợ.")
                    time.sleep(2)
                    driver.quit()
                    return
            else:
                print("Không thấy Captcha (hoặc đã biến mất).")
                break
        except Exception:
            break
        
        time.sleep(1)

    # Chờ Login thành công
    print("Đang chờ xác nhận đăng nhập...")
    try:
        profile_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="profile-icon"]'))
        )
        print("✅ Đăng nhập thành công!")
        cookies = driver.get_cookies()
    except TimeoutException:
        print("Hết thời gian chờ hoặc Login thất bại.")

    time.sleep(5)
    driver.quit()

