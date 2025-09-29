from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Load test data from JSON file
with open('test_data.json', 'r') as file:
    test_data = json.load(file)

user_data = test_data["user_data"]
payment_data = test_data["payment_data"]

# Initialize driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_experimental_option("detach", True)  # Keep browser open after script
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the registration page
driver.get("https://qaapiv4.sikkasoft.com/v4/portal/authentication/sai-register?request=apiplusplus&redirect_url=https://webhook.site/3b642c46-01ab-4bd7-b9c0-e4104c76df5b&callback_key=sikkauser&project_id=6758339")

# ✅ Close popup if present
try:
    close_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "interactive-close-button"))
    )
    close_btn.click()
    print("Popup closed successfully")
except:
    print("No popup found, continuing...")

# Fill form fields
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "first_name")))

# Fill registration form using JSON data
driver.find_element(By.NAME, "first_name").send_keys(user_data["first_name"])
driver.find_element(By.NAME, "last_name").send_keys(user_data["last_name"])
driver.find_element(By.NAME, "username").send_keys(user_data["username"])
driver.find_element(By.NAME, "password").send_keys(user_data["password"])
driver.find_element(By.NAME, "confirm_password").send_keys(user_data["confirm_password"])
driver.find_element(By.NAME, "phoneNumber").send_keys(user_data["phoneNumber"])
driver.find_element(By.NAME, "dev_address").send_keys(user_data["dev_address"])

# Country dropdown
country_dropdown = Select(driver.find_element(By.NAME, "dev_country"))
country_dropdown.select_by_visible_text(user_data["dev_country"])

driver.find_element(By.NAME, "dev_city").send_keys(user_data["dev_city"])
driver.find_element(By.NAME, "dev_state").send_keys(user_data["dev_state"])
driver.find_element(By.NAME, "dev_zip").send_keys(user_data["dev_zip"])

# Click checkbox (agree to terms)
checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
driver.execute_script("arguments[0].click();", checkbox)

# ✅ Click Continue button
continue_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sai_button.btn.btn-secondary"))
)
continue_btn.click()

print("Continue button clicked, moving to payment page...")

# --- PAYMENT PAGE ---
# Wait for payment form to load
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "credit_card_number")))

# Fill payment form using JSON data
driver.find_element(By.NAME, "credit_card_number").send_keys(payment_data["credit_card_number"])
driver.find_element(By.NAME, "credit_card_expiration_date").send_keys(payment_data["credit_card_expiration_date"])
driver.find_element(By.NAME, "credit_security_code").send_keys(payment_data["credit_security_code"])

# ✅ Click Register button
register_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
)
# register_btn.click()  # Uncomment to actually submit

print("Registration submitted!")

time.sleep(5)  # Let user see result

# Close the browser
driver.quit()