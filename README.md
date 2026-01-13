
### 2. Clone project
```bash
git clone <repository-url>
```

### 3. Tạo virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\Activate
```

### 4. Cài đặt dependencies
```bash
pip install selenium webdriver-manager requests Pillow pydantic
```

## Sử dụng

### 1. Cấu hình thông tin đăng nhập

Chỉnh sửa file `run_example.py`:
```python
EMAIL = "your_email@example.com"  
PASSWORD = "your_password"
```

### 2. Chạy tool
```bash
python run_example.py
```
