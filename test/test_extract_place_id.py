from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from crawlers.get_review_content import extract_place_id

def test_extract_place_id():
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # WebDriver 초기화
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # 테스트할 장소 검색
        keyword = "춘천 명동 카페"
        driver.get(f"https://map.naver.com/v5/search/{keyword}")
        
        # 장소 ID 추출 테스트
        place_id = extract_place_id(keyword, driver)
        print(f"추출된 장소 ID: {place_id}")
        
    finally:
        # WebDriver 종료
        driver.quit()

if __name__ == "__main__":
    test_extract_place_id() 