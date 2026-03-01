"""
Moodle Data Fetcher Module
Handles Selenium automation for Moodle data extraction
"""

import time
import json
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging


class MoodleFetcher:
    """Handles Moodle automation and data extraction"""
    
    def __init__(self, headless: bool = True, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.driver = None
        self.wait = None
        self.captured_data = {
            "courses": [],
            "events": [],
            "notifications": [],
            "recent_courses": [],
            "calendar": [],
            "session": {}
        }
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        options = Options()
        
        # Enable performance logging for network interception
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL', 'browser': 'ALL'}
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        
        # Add slow motion simulation
        if self.slow_mo > 0:
            options.add_argument(f'--force-device-scale-factor=1')
        
        # Set up logging
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def check_login_status(self):
        """Check if login was successful"""
        try:
            # Check for user menu
            user_menu = self.driver.find_elements(By.CSS_SELECTOR, '.usermenu')
            if user_menu:
                user_menu_text = user_menu[0].text
                if 'You are not logged in' in user_menu_text:
                    return False, "Not logged in"
                else:
                    # Try to extract user info
                    try:
                        user_name = self.driver.find_element(
                            By.CSS_SELECTOR, '.usertext, .usermenu .login, [data-usermenu]'
                        ).text
                        return True, f"Logged in as: {user_name}"
                    except:
                        return True, "Logged in successfully"
            
            # Check dashboard elements
            dashboard_elements = self.driver.find_elements(
                By.CSS_SELECTOR, '.dashboard, .course-list, .block'
            )
            if dashboard_elements:
                return True, "On dashboard"
            
            # Check current URL
            current_url = self.driver.current_url
            if 'login' not in current_url and 'index' not in current_url:
                return True, f"On page: {current_url}"
            
            return False, "Login status unknown"
        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False, str(e)
    
    def extract_network_data(self):
        """Extract data from network logs"""
        try:
            logs = self.driver.get_log('performance')
            
            for entry in logs:
                try:
                    log = json.loads(entry['message'])['message']
                    
                    # Check for network responses
                    if log['method'] == 'Network.responseReceived':
                        request_id = log['params']['requestId']
                        url = log['params']['response']['url']
                        
                        # Get response body
                        try:
                            response = self.driver.execute_cdp_cmd(
                                'Network.getResponseBody',
                                {'requestId': request_id}
                            )
                            
                            if response and 'body' in response:
                                body = response['body']
                                
                                # Parse JSON if applicable
                                if 'application/json' in log['params']['response'].get('mimeType', ''):
                                    try:
                                        data = json.loads(body)
                                        
                                        # Categorize based on URL
                                        if 'core_course_get_enrolled_courses_by_timeline_classification' in url:
                                            self.captured_data['courses'] = data
                                            self.logger.info("Captured enrolled courses")
                                        
                                        elif 'core_calendar_get_calendar_monthly_view' in url:
                                            self.captured_data['calendar'].append(data)
                                            self.logger.info("Captured calendar data")
                                        
                                        elif 'core_course_get_recent_courses' in url:
                                            self.captured_data['recent_courses'] = data
                                            self.logger.info("Captured recent courses")
                                        
                                        elif 'core_fetch_notifications' in url:
                                            self.captured_data['notifications'] = data.get('notifications', data)
                                            self.logger.info("Captured notifications")
                                        
                                        elif 'core_calendar_get_action_events_by_timesort' in url:
                                            self.captured_data['events'] = data.get('events', data)
                                            self.logger.info("Captured calendar events")
                                    
                                    except json.JSONDecodeError:
                                        pass
                        except:
                            pass
                except:
                    continue
        except Exception as e:
            self.logger.error(f"Error extracting network data: {e}")
    
    def login(self, username: str, password: str, moodle_url: str) -> Dict[str, Any]:
        """Login to Moodle and fetch data"""
        try:
            self.setup_driver()
            
            # Navigate to login page
            login_url = f"{moodle_url.rstrip('/')}/login/index.php"
            self.logger.info(f"Navigating to {login_url}")
            self.driver.get(login_url)
            
            # Wait for login form
            self.wait.until(EC.presence_of_element_located((By.ID, "login")))
            
            # Get login token
            try:
                login_token = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[name="logintoken"]'
                ).get_attribute('value')
                self.logger.info(f"Login token found")
            except:
                login_token = None
            
            # Fill credentials
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_btn = self.driver.find_element(By.ID, "loginbtn")
            login_btn.click()
            
            # Wait for navigation
            time.sleep(5)
            
            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "body")
                )
            )
            
            # Check login status
            login_success, status_message = self.check_login_status()
            
            if login_success:
                # Wait for API calls
                time.sleep(8)
                
                # Extract network data
                self.extract_network_data()
                
                # Get cookies
                cookies = self.driver.get_cookies()
                for cookie in cookies:
                    if 'MoodleSession' in cookie['name']:
                        self.captured_data['session'] = {
                            'name': cookie['name'],
                            'value': cookie['value'][:20] + '...',
                            'expires': cookie.get('expiry'),
                            'domain': cookie.get('domain')
                        }
            
            return {
                'success': login_success,
                'message': status_message,
                'data': self.captured_data,
                'url': self.driver.current_url,
                'title': self.driver.title
            }
            
        except TimeoutException as e:
            self.logger.error(f"Timeout during login: {e}")
            return {
                'success': False,
                'message': f"Timeout: {str(e)}",
                'data': self.captured_data
            }
        except WebDriverException as e:
            self.logger.error(f"WebDriver error: {e}")
            return {
                'success': False,
                'message': f"Browser error: {str(e)}",
                'data': self.captured_data
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}",
                'data': self.captured_data
            }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()