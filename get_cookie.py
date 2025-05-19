from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import yaml

def setup_driver():
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式，如果需要可以取消注释
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 设置并启动WebDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def login_and_get_cookie(driver, username, password):
    try:
        # 等待用户名输入框加载
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/form/div/div/div[2]/div[3]/div[1]/div[1]/input[1]'))
        )
        # 等待密码输入框加载
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/form/div/div/div[2]/div[3]/div[1]/div[1]/input[2]'))
        )
        
        # 输入用户名和密码
        username_input.send_keys(username)
        password_input.send_keys(password)
        
        # 点击登录按钮
        login_button = driver.find_element(By.XPATH, '/html/body/form/div/div/div[2]/div[3]/div[1]/div[1]/span/input')
        login_button.click()
        
        # 等待登录完成
        WebDriverWait(driver, 10).until(
            lambda driver: driver.current_url != "https://zhlgd.whut.edu.cn/tp_up/view?m=up#act=up/appstore/applist"
        )
        
        time.sleep(1)
        # 点击电费查询按钮
        electricity_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div/div[2]/div/div/div[4]/div[27]'))
        )
        electricity_button.click()
        
        # 切换到新打开的标签页
        # 获取所有窗口句柄
        all_handles = driver.window_handles
        # 切换到最新打开的标签页
        driver.switch_to.window(all_handles[-1])
        
        # 等待1秒
        time.sleep(1)
        
        # 点击宿舍选择按钮
        dorm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/ul/li[7]/a/div/img'))
        )
        dorm_button.click()
        
        # 等待页面加载完成
        time.sleep(1)
        
        # 获取所有cookie
        cookies = driver.get_cookies()
        return cookies
        
    except Exception as e:
        print(f"操作过程中出现错误: {str(e)}")
        return None

def get_jsessionid():
    # 获取WebDriver实例
    driver = setup_driver()
    
    try:
        # 打开目标网页
        url = "https://zhlgd.whut.edu.cn/tp_up/view?m=up#act=up/appstore/applist"
        driver.get(url)
        print("成功打开登录页面")
        
        # 在这里输入您的用户名和密码
        with open('user_settings.yaml', 'r', encoding='utf-8') as file:
            settings = yaml.safe_load(file)
        username = settings.get('USER_NAME')
        password = settings.get('PASSWORD')
        cookies = login_and_get_cookie(driver, username, password)
        
        if cookies:
            # 查找JSESSIONID
            for cookie in cookies:
                if cookie['name'] == 'JSESSIONID':
                    return cookie['value']
            print("未找到JSESSIONID")
            return None
        else:
            print("获取Cookie失败")
            return None
            
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    jsessionid = get_jsessionid()
    if jsessionid:
        print(f"JSESSIONID: {jsessionid}")