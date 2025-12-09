"""
Grok Video Generation Automation Script (Windows)
Connects to your EXISTING Chrome browser - No new window!
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import json
import os
import sys
from datetime import datetime
import socket
import urllib.request
import urllib.error
import glob
import csv
def extract_demographics(text):
    """
    Extract race and gender from a text description.
    Returns a tuple of (race_code, gender_code)
    """
    text_lower = text.lower()
    
    # Define race keywords and their codes
    race_map = {
        'asian': 'A',
        'black': 'B',
        'african': 'B',
        'white': 'W',
        'caucasian': 'W',
        'hispanic': 'H',
        'latino': 'H',
        'latina': 'H',
        'indian': 'I',
        'middle eastern': 'M',
        'arab': 'M'
    }
    
    # Define gender keywords and their codes
    gender_map = {
        'woman': 'F',
        'female': 'F',
        'girl': 'F',
        'man': 'M',
        'male': 'M',
        'boy': 'M'
    }
    
    # Find race
    race_code = "None"
    for keyword, code in race_map.items():
        if keyword in text_lower:
            race_code = code
            break
    
    # Find gender
    gender_code = "None"
    for keyword, code in gender_map.items():
        if keyword in text_lower:
            gender_code = code
            break
    
    return race_code, gender_code




# Try to import undetected-chromedriver for Cloudflare bypass
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("⚠ undetected-chromedriver not installed. Install it for better Cloudflare bypass:")
    print("   pip install undetected-chromedriver")

class GrokVideoAutomation:
    def __init__(self, use_existing_browser=True, debugger_port=9222):
        """
        Initialize automation
        
        Args:
            use_existing_browser: Connect to existing Chrome instead of opening new
            debugger_port: Port for Chrome remote debugging (default: 9222)
        """
        self.use_existing_browser = use_existing_browser
        self.debugger_port = debugger_port
        self.driver = None
        # Remote drive path (RaiDrive mounted)
        self.download_dir = r"V:\media\NAS\DATASET\GenAI_600\created_human_videos\Grok\binh"  
        
        # Ensure download directory exists (works with remote drives too)
        try:
            os.makedirs(self.download_dir, exist_ok=True)
            if os.path.exists(self.download_dir):
                print(f"✓ Download directory ready: {self.download_dir}")
            else:
                print(f"⚠ Download directory may not be accessible: {self.download_dir}")
                print("  Make sure the remote drive (RaiDrive) is connected")
        except Exception as e:
            print(f"⚠ Could not verify download directory: {e}")
            print(f"  Path: {self.download_dir}")
            print("  Make sure the remote drive (RaiDrive) is connected and accessible")
    
    def check_debugging_port(self):
        """Check if Chrome remote debugging is available on the port"""
        try:
            # Try to connect to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.debugger_port))
            sock.close()
            
            if result == 0:
                # Port is open, try to access the JSON endpoint
                try:
                    response = urllib.request.urlopen(
                        f'http://127.0.0.1:{self.debugger_port}/json',
                        timeout=2
                    )
                    return True
                except urllib.error.URLError:
                    return False
            return False
        except Exception:
            return False
        
    def start_browser(self):
        """Connect to existing Chrome browser"""
        try:
            if self.use_existing_browser:
                print("Checking if Chrome remote debugging is enabled...")
                
                # Check if debugging port is available
                if not self.check_debugging_port():
                    print(f"\n✗ Chrome remote debugging is NOT enabled on port {self.debugger_port}")
                    print("\n" + "="*60)
                    print("PROBLEM DETECTED:")
                    print("="*60)
                    print("Your Chrome browser is NOT running with remote debugging enabled.")
                    print("\nThis happens when you open Chrome normally (without the debugging flag).")
                    print("\nSOLUTION:")
                    print("="*60)
                    print("1. Close ALL Chrome windows completely")
                    print("2. Start Chrome with remote debugging using ONE of these methods:")
                    print("\n   Method A: Use the batch file (EASIEST)")
                    print("   - Run: start_chrome_debug.bat")
                    print("   - (This file will be created if it doesn't exist)")
                    print("\n   Method B: Command line")
                    print(f'   - Open PowerShell/CMD and run:')
                    print(f'   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port={self.debugger_port} --user-data-dir="C:\\ChromeDebug"')
                    print("\n   Method C: Create a shortcut")
                    print("   - Right-click Desktop → New → Shortcut")
                    print('   - Paste the command from Method B')
                    print("\n3. Login to Grok/X in that Chrome window")
                    print("4. Run this script again")
                    print("="*60)
                    
                    # Auto-create batch file if it doesn't exist
                    batch_file = "start_chrome_debug.bat"
                    if not os.path.exists(batch_file):
                        self.create_batch_file(batch_file)
                        print(f"\n✓ Created '{batch_file}' for you!")
                        print(f"  Just double-click it to start Chrome with debugging enabled.")
                    
                    sys.exit(1)
                
                print("✓ Remote debugging port is active!")
                print("Connecting to your existing Chrome browser...")
                
                options = Options()
                # When connecting to existing browser, only debuggerAddress is needed
                # Command-line args must be set when Chrome starts, not when connecting
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debugger_port}")
                
                # Set download preferences for automatic download
                # Note: These may not work when connecting to existing browser,
                # but we'll also use CDP to set download behavior
                prefs = {
                    "download.default_directory": self.download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                options.add_experimental_option("prefs", prefs)
                
                # Try with webdriver-manager first
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as e:
                    print(f"  Note: {e}")
                    # Fallback without webdriver-manager
                    self.driver = webdriver.Chrome(options=options)
                
                # Execute script to remove webdriver property (helps with detection)
                try:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except:
                    pass  # Ignore if script fails
                
                # Set download behavior using Chrome DevTools Protocol
                try:
                    # Convert Windows path to format Chrome CDP expects
                    download_path = os.path.normpath(self.download_dir)
                    self.driver.execute_cdp_cmd('Browser.setDownloadBehavior', {
                        'behavior': 'allow',
                        'downloadPath': download_path
                    })
                    print(f"✓ Configured automatic downloads to: {self.download_dir}")
                except Exception as e:
                    print(f"⚠ Could not set download behavior via CDP: {e}")
                    print(f"  Trying to use path: {self.download_dir}")
                    print("  Downloads may still prompt for save location")
                    print("  Note: CDP may not work with remote drives (RaiDrive)")
                
                print("✓ Connected to existing Chrome browser!")
                print(f"  Current URL: {self.driver.current_url}")
                
            else:
                # Fallback to opening new browser - use undetected-chromedriver if available
                print("Opening new Chrome browser...")
                if UC_AVAILABLE:
                    print("  Using undetected-chromedriver for Cloudflare bypass...")
                    options = uc.ChromeOptions()
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--no-sandbox")
                    self.driver = uc.Chrome(options=options, version_main=None)
                else:
                    options = Options()
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    self.driver = webdriver.Chrome(options=options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✓ New browser opened")
            
            self.wait = WebDriverWait(self.driver, 30)
            
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Failed to connect to browser: {error_msg}")
            print("\n" + "="*60)
            print("CONNECTION ERROR:")
            print("="*60)
            print("Even though the port seems open, Selenium couldn't connect.")
            print(f"\nError details: {error_msg}")
            print("\nPossible causes:")
            print("1. Chrome was started with debugging but crashed")
            print("2. Another process is using port 9222")
            print("3. ChromeDriver version mismatch")
            print("4. Chrome needs to be restarted with debugging enabled")
            print("\nTry:")
            print("1. Close ALL Chrome windows completely")
            print("2. Restart Chrome with: start_chrome_debug.bat")
            print("3. Wait a few seconds for Chrome to fully start")
            print("4. Run this script again")
            print("="*60)
            sys.exit(1)
    
    def create_batch_file(self, filename):
        """Create a batch file to start Chrome with debugging"""
        batch_content = f'''@echo off
echo Starting Chrome with Remote Debugging...
echo.
echo IMPORTANT: Close ALL other Chrome windows first!
echo.
timeout /t 3 /nobreak >nul
start "" "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port={self.debugger_port} --user-data-dir="C:\\ChromeDebug"
echo.
echo Chrome is now running with automation support on port {self.debugger_port}
echo You can close this window
pause
'''
        try:
            with open(filename, "w") as f:
                f.write(batch_content)
        except Exception as e:
            print(f"Could not create batch file: {e}")
    
    def check_cloudflare(self):
        """Check if Cloudflare challenge is present and wait for it to complete"""
        try:
            # Check for Cloudflare challenge indicators
            page_source = self.driver.page_source.lower()
            page_title = self.driver.title.lower()
            
            cloudflare_indicators = [
                "checking your browser",
                "just a moment",
                "cloudflare",
                "ddos protection",
                "ray id",
                "cf-browser-verification"
            ]
            
            is_cloudflare = any(indicator in page_source or indicator in page_title 
                              for indicator in cloudflare_indicators)
            
            if is_cloudflare:
                print("⏳ Cloudflare challenge detected, waiting for verification...")
                max_wait = 30  # Wait up to 30 seconds
                waited = 0
                
                while waited < max_wait:
                    time.sleep(2)
                    waited += 2
                    current_source = self.driver.page_source.lower()
                    current_title = self.driver.title.lower()
                    
                    # Check if Cloudflare challenge is gone
                    still_challenging = any(indicator in current_source or indicator in current_title 
                                          for indicator in cloudflare_indicators)
                    
                    if not still_challenging:
                        print("✓ Cloudflare challenge passed!")
                        time.sleep(2)  # Give page time to load
                        return True
                    
                    print(f"   ... still waiting ({waited}s/{max_wait}s)")
                
                print("⚠ Cloudflare challenge may still be active")
                return False
            
            return True
        except Exception as e:
            print(f"⚠ Error checking Cloudflare: {e}")
            return True  # Continue anyway
    
    def navigate_to_grok(self):
        """Check if ready (assumes you're already on imagine tab)"""
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check if on Grok
        if "grok" not in current_url.lower() and "grok.com" not in current_url:
            print("\n" + "="*60)
            print("⚠ NOT ON GROK PAGE")
            print("="*60)
            print("Please make sure you have:")
            print("1. Run start_chrome_debug.bat")
            print("2. Manually opened grok.com in that Chrome window")
            print("3. Navigated to the 'Imagine' tab")
            print("4. Logged in to Grok")
            print("5. Then run this script")
            print("="*60)
            return False
        
        # Check if input area is available (try multiple selectors)
        try:
            time.sleep(2)  # Wait for page to fully load
            
            # Try multiple selectors to find the input element
            input_selectors = [
                (By.XPATH, "//*[@placeholder and contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'imagine')]"),
                (By.XPATH, "//*[@placeholder and contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'type')]"),
                (By.XPATH, "//*[@contenteditable='true']"),
                (By.XPATH, "//div[@contenteditable='true']"),
                (By.TAG_NAME, "textarea"),
                (By.TAG_NAME, "input"),
                (By.XPATH, "//*[contains(@class, 'input') or contains(@class, 'prompt') or contains(@class, 'text')]"),
            ]
            
            input_found = False
            for selector_type, selector_value in input_selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if element:
                        print(f"✓ Ready! Input area found using: {selector_type}")
                        input_found = True
                        break
                except:
                    continue
            
            if input_found:
                return True
            else:
                raise Exception("No input element found")
        except:
            print("\n✗ Input area not found!")
            print(f"  Current URL: {self.driver.current_url}")
            print("  Please make sure you're on the Imagine tab and the page is fully loaded.")
            print("  The input box should be visible at the bottom with 'Type to imagine' placeholder.")
            return False
    
    def generate_video(self, prompt, wait_time=180):
        """Generate a video: input prompt, wait, download, and go back"""
        print(f"\n📹 Generating video: {prompt[:60]}...")
        
        try:
            # Find the input element (fresh page after going back)
            print("🔍 Looking for input area...")
            
            input_selectors = [
                (By.XPATH, "//*[@placeholder and contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'imagine')]"),
                (By.XPATH, "//*[@placeholder and contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'type')]"),
                (By.XPATH, "//*[@contenteditable='true']"),
                (By.XPATH, "//div[@contenteditable='true']"),
                (By.TAG_NAME, "textarea"),
                (By.TAG_NAME, "input"),
                (By.XPATH, "//*[contains(@class, 'input') or contains(@class, 'prompt') or contains(@class, 'text')]"),
            ]
            
            input_element = None
            for selector_type, selector_value in input_selectors:
                try:
                    input_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if input_element:
                        print(f"✓ Found input area using: {selector_type}")
                        break
                except:
                    continue
            
            if not input_element:
                raise Exception("Could not find input element")
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", input_element)
            time.sleep(0.5)
            
            # Click to focus
            input_element.click()
            time.sleep(0.5)
            
            # Clear any existing text
            try:
                # Try clear() first (works for input/textarea)
                input_element.clear()
            except:
                # For contenteditable divs, select all and delete
                try:
                    input_element.send_keys(Keys.CONTROL + "a")
                    input_element.send_keys(Keys.DELETE)
                except:
                    # Alternative: use JavaScript to clear
                    self.driver.execute_script("arguments[0].textContent = '';", input_element)
            time.sleep(0.3)
            
            # Type the prompt (no /imagine prefix needed - you're already on imagine tab)
            print(f"📝 Typing prompt: {prompt[:50]}...")
            
            # Type the prompt naturally
            for char in prompt:
                input_element.send_keys(char)
                time.sleep(0.02)  # Natural typing speed
            
            time.sleep(1)
            
            # Submit - look for submit button first (the arrow icon on the right)
            print("⏳ Submitting prompt...")
            try:
                # Try to find submit button (arrow icon or send button)
                submit_selectors = [
                    (By.XPATH, "//button[contains(@aria-label, 'Send') or contains(@aria-label, 'Submit') or contains(@aria-label, 'send')]"),
                    (By.XPATH, "//button[@type='submit']"),
                    (By.XPATH, "//*[contains(@class, 'send') or contains(@class, 'submit')]//button"),
                    (By.XPATH, "//button[.//*[contains(@class, 'arrow') or contains(@class, 'send')]]"),
                ]
                
                submit_button = None
                for sel_type, sel_value in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(sel_type, sel_value)
                        if submit_button:
                            submit_button.click()
                            print("✓ Clicked submit button")
                            break
                    except:
                        continue
                
                # If no button found, try Enter key
                if not submit_button:
                    input_element.send_keys(Keys.RETURN)
                    print("✓ Sent Enter key")
            except Exception as e:
                # Last resort: try Enter key
                try:
                    input_element.send_keys(Keys.RETURN)
                    print("✓ Sent Enter key (fallback)")
                except:
                    print(f"⚠ Could not submit: {e}")
            
            # Wait a bit for video generation to start
            print("⏳ Waiting for video generation to start...")
            time.sleep(45)  # Initial wait
            
            # Check if download button appears (video is ready)
            print("🔍 Checking if video is ready (looking for download button)...")
            used_photo_method = False
            
            if self.check_video_ready_by_download_button():
                print("✓ Video is ready! Download button found.")
            else:
                # Download button not found or not working after 20 seconds
                print("⚠ Video generation failed or taking too long")
                print("   Trying alternative method: generate video from photo...")
                used_photo_method = self.generate_video_from_photo()
            
            if used_photo_method:
                print("✓ Video generation complete (from photo)!")
            else:
                print("✓ Video generation complete!")
            
            # Download the video
            download_result = self.download_video(prompt)
            
            # If video was successfully downloaded, save prompt to CSV
            if download_result and isinstance(download_result, tuple):
                download_success, video_name = download_result
                if download_success and video_name:
                    method_used = "photo" if used_photo_method else "text"
                    self.save_successful_prompt(prompt, method_used, video_name)
            
            # Go back to imagine tab for next prompt
            # If we used photo method, need to go back twice
            self.go_back_to_imagine_tab(go_back_twice=used_photo_method)
            
            return True
            
        except Exception as e:
            print(f"✗ Error generating video: {e}")
            self.take_screenshot(f"error_{int(time.time())}.png")
            return False
    
    def count_existing_videos(self):
        """Count existing MP4 videos in download directory"""
        try:
            if not os.path.exists(self.download_dir):
                return 0
            
            # Count MP4 files matching the pattern Gr-binh-*-*-*.mp4 (with race and gender codes)
            pattern = os.path.join(self.download_dir, "Gr-binh-*-*-*.mp4")
            existing_files = glob.glob(pattern)
            return len(existing_files)
        except Exception as e:
            print(f"⚠ Error counting existing videos: {e}")
            return 0
    
    def get_next_video_filename(self, prompt):
        """Get the next sequential video filename with race and gender codes"""
        # Extract demographics from prompt
        race_code, gender_code = extract_demographics(prompt)
        
        # Count existing videos
        n_exist_videos = self.count_existing_videos()
        next_number = n_exist_videos + 1
        
        # Format: Gr-binh-<index>-<race-code>-<gender-code>.mp4
        filename = f"Gr-binh-{next_number}-{race_code}-{gender_code}.mp4"
        return filename, next_number
    
    def rename_downloaded_file(self, expected_filename, max_wait=20):
        """Wait for download to complete and rename the file"""
        try:
            print(f"📁 Waiting for download to complete and renaming to: {expected_filename}")
            expected_path = os.path.join(self.download_dir, expected_filename)
            
            # Wait for a new file to appear in the download directory
            initial_files = set()
            try:
                if os.path.exists(self.download_dir):
                    initial_files = set(os.listdir(self.download_dir))
            except:
                pass
            
            # Wait for new file to appear
            waited = 0
            new_file = None
            while waited < max_wait:
                time.sleep(2)
                waited += 2
                
                try:
                    if os.path.exists(self.download_dir):
                        current_files = set(os.listdir(self.download_dir))
                        new_files = current_files - initial_files
                        
                        # Look for new MP4 files
                        for file in new_files:
                            if file.lower().endswith('.mp4'):
                                new_file = os.path.join(self.download_dir, file)
                                # Check if file is still being written (size stable)
                                try:
                                    size1 = os.path.getsize(new_file)
                                    time.sleep(1)
                                    size2 = os.path.getsize(new_file)
                                    if size1 == size2 and size1 > 0:
                                        # File is complete, rename it
                                        if new_file != expected_path:
                                            os.rename(new_file, expected_path)
                                            print(f"✓ Renamed: {file} → {expected_filename}")
                                        else:
                                            print(f"✓ File already named correctly: {expected_filename}")
                                        return True
                                except:
                                    continue
                except:
                    pass
                
                if waited % 10 == 0:
                    print(f"   ... waiting for download ({waited}s/{max_wait}s)")
            
            # If we didn't find a new file, try to find the most recent MP4
            if not new_file:
                try:
                    if os.path.exists(self.download_dir):
                        mp4_files = glob.glob(os.path.join(self.download_dir, "*.mp4"))
                        if mp4_files:
                            # Get the most recently modified file
                            latest_file = max(mp4_files, key=os.path.getmtime)
                            if latest_file != expected_path:
                                os.rename(latest_file, expected_path)
                                print(f"✓ Renamed latest file to: {expected_filename}")
                                return True
                except Exception as e:
                    print(f"⚠ Could not rename file: {e}")
            
            print(f"⚠ Could not find or rename downloaded file")
            print(f"  Expected: {expected_filename}")
            return False
            
        except Exception as e:
            print(f"⚠ Error renaming downloaded file: {e}")
            return False
    
    def download_video(self, prompt):
        """Download the generated video automatically to specified directory with sequential naming"""
        try:
            # Get the next filename (with race and gender codes extracted from prompt)
            expected_filename, video_number = self.get_next_video_filename(prompt)
            print(f"📹 Will save as: {expected_filename} (Video #{video_number})")
            
            print("🔍 Looking for video download button...")
            time.sleep(2)  # Wait a bit for video to appear
            
            # Try multiple selectors for download button
            download_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'download') or contains(@aria-label, 'Download')]"),
                (By.XPATH, "//a[contains(@aria-label, 'download') or contains(@aria-label, 'Download')]"),
                (By.XPATH, "//button[contains(@title, 'download') or contains(@title, 'Download')]"),
                (By.XPATH, "//a[contains(@title, 'download') or contains(@title, 'Download')]"),
                (By.XPATH, "//*[contains(@class, 'download')]"),
                (By.CSS_SELECTOR, "button[aria-label*='download' i]"),
                (By.CSS_SELECTOR, "a[aria-label*='download' i]"),
                (By.XPATH, "//button[.//*[contains(@class, 'download')]]"),
                (By.XPATH, "//a[.//*[contains(@class, 'download')]]")
            ]
            
            download_button = None
            for selector_type, selector_value in download_selectors:
                try:
                    download_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if download_button:
                        print(f"✓ Found download button!")
                        break
                except:
                    continue
            
            if download_button:
                # Ensure download behavior is set (in case it wasn't set during connection)
                try:
                    # Convert Windows path to format Chrome CDP expects
                    download_path = os.path.normpath(self.download_dir)
                    self.driver.execute_cdp_cmd('Browser.setDownloadBehavior', {
                        'behavior': 'allow',
                        'downloadPath': download_path
                    })
                    print(f"✓ Download path configured: {self.download_dir}")
                except Exception as e:
                    print(f"⚠ Could not set download path via CDP: {e}")
                    print(f"  Path: {self.download_dir}")
                    print("  Chrome may prompt for save location")
                
                # Scroll to button
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
                time.sleep(1)
                
                # Click download button
                print("⬇️ Clicking download button...")
                try:
                    download_button.click()
                except:
                    self.driver.execute_script("arguments[0].click();", download_button)
                
                print(f"✓ Download initiated! File will be saved to: {self.download_dir}")
                
                # Wait for download and rename file
                rename_success = self.rename_downloaded_file(expected_filename)
                # Return both success status and video filename
                return (rename_success, expected_filename) if rename_success else (False, None)
            else:
                print("⚠ Download button not found automatically")
                print("  You may need to download the video manually")
                print("  Look for a download icon/button near the generated video")
                print(f"  Save location: {self.download_dir}")
                return (False, None)
                
        except Exception as e:
            print(f"⚠ Could not download video automatically: {e}")
            print("  You may need to download it manually from the browser")
            print(f"  Save location: {self.download_dir}")
            return (False, None)
    
    def check_video_ready_by_download_button(self):
        """Check if video is ready by trying to click download button and verifying download starts"""
        try:
            # Get list of existing files before clicking download
            initial_files = set()
            try:
                if os.path.exists(self.download_dir):
                    initial_files = set(os.listdir(self.download_dir))
            except:
                pass
            
            # Try to find download button
            download_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'download') or contains(@aria-label, 'Download')]"),
                (By.XPATH, "//a[contains(@aria-label, 'download') or contains(@aria-label, 'Download')]"),
                (By.XPATH, "//button[contains(@title, 'download') or contains(@title, 'Download')]"),
                (By.XPATH, "//a[contains(@title, 'download') or contains(@title, 'Download')]"),
                (By.XPATH, "//*[contains(@class, 'download')]"),
                (By.CSS_SELECTOR, "button[aria-label*='download' i]"),
                (By.CSS_SELECTOR, "a[aria-label*='download' i]"),
                (By.XPATH, "//button[.//*[contains(@class, 'download')]]"),
                (By.XPATH, "//a[.//*[contains(@class, 'download')]]")
            ]
            
            # Wait up to 30 seconds for download button to appear and be clickable
            download_button = None
            for selector_type, selector_value in download_selectors:
                try:
                    download_button = WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if download_button:
                        print("✓ Download button found and clickable!")
                        break
                except:
                    continue
            
            if not download_button:
                print("⚠ Download button not found or not clickable after 20 seconds")
                return False
            
            # Try clicking the download button to see if download actually starts
            print("🖱️ Testing download button click...")
            try:
                # Scroll button into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
                time.sleep(0.5)
                
                # Click the button
                try:
                    download_button.click()
                except:
                    self.driver.execute_script("arguments[0].click();", download_button)
                
                # Wait a few seconds to see if download actually started
                print("   Waiting 10 seconds to check if download started...")
                time.sleep(10)
                
                # Check if new file appeared in download directory
                try:
                    if os.path.exists(self.download_dir):
                        current_files = set(os.listdir(self.download_dir))
                        new_files = current_files - initial_files
                        
                        # Check for new MP4 files or .crdownload files (Chrome download in progress)
                        for file in new_files:
                            if file.lower().endswith('.mp4') or file.lower().endswith('.crdownload'):
                                print("✓ Download started! Video is ready.")
                                return True
                except:
                    pass
                
                # If no new file, video might not be ready yet
                print("⚠ Download button clicked but no download started")
                print("   Video may still be generating...")
                return False
                
            except Exception as e:
                print(f"⚠ Error clicking download button: {e}")
                return False
            
        except Exception as e:
            print(f"⚠ Error checking download button: {e}")
            return False
    
    def generate_video_from_photo(self):
        """Generate video from first photo by scrolling down and clicking Make video"""
        try:
            print("📸 Scrolling down to find generated photos...")
            
            # Scroll down to see generated photos
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)
            
            # Try to find the first photo/image
            photo_selectors = [
                (By.XPATH, "//img[contains(@class, 'image') or contains(@class, 'photo') or contains(@class, 'picture')]"),
                (By.XPATH, "//*[contains(@class, 'image') or contains(@class, 'photo')]//img"),
                (By.XPATH, "//img[not(contains(@src, 'icon')) and not(contains(@src, 'logo'))]"),
                (By.CSS_SELECTOR, "img"),
            ]
            
            first_photo = None
            for selector_type, selector_value in photo_selectors:
                try:
                    photos = self.driver.find_elements(selector_type, selector_value)
                    # Filter out small icons/logos and find a substantial image
                    for photo in photos:
                        try:
                            # Check if image is visible and reasonably sized
                            if photo.is_displayed():
                                size = photo.size
                                if size['width'] > 100 and size['height'] > 100:
                                    first_photo = photo
                                    break
                        except:
                            continue
                    if first_photo:
                        break
                except:
                    continue
            
            if not first_photo:
                print("⚠ Could not find a suitable photo")
                return False
            
            print("✓ Found first photo, clicking on it...")
            # Scroll photo into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_photo)
            time.sleep(1)
            
            # Click on the photo
            try:
                first_photo.click()
            except:
                self.driver.execute_script("arguments[0].click();", first_photo)
            
            time.sleep(2)
            
            # Look for "Make video" button
            print("🔍 Looking for 'Make video' button...")
            make_video_selectors = [
                (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'make video')]"),
                (By.XPATH, "//button[contains(text(), 'Make video')]"),
                (By.XPATH, "//button[contains(text(), 'make video')]"),
                (By.XPATH, "//*[contains(@aria-label, 'make video') or contains(@aria-label, 'Make video')]"),
                (By.XPATH, "//button[contains(@class, 'video')]"),
            ]
            
            make_video_button = None
            for selector_type, selector_value in make_video_selectors:
                try:
                    make_video_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if make_video_button:
                        print("✓ Found 'Make video' button!")
                        break
                except:
                    continue
            
            if make_video_button:
                # Scroll button into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", make_video_button)
                time.sleep(1)
                
                # Click "Make video" button
                print("🎬 Clicking 'Make video' button...")
                try:
                    make_video_button.click()
                except:
                    self.driver.execute_script("arguments[0].click();", make_video_button)
                
                print("⏳ Waiting for video generation from photo...")
                time.sleep(30)  # Wait for video generation
                print("✓ Video generation from photo should be complete!")
                return True
            else:
                print("⚠ Could not find 'Make video' button")
                return False
                
        except Exception as e:
            print(f"⚠ Error generating video from photo: {e}")
            return False
    
    def save_successful_prompt(self, prompt, method_used="text", video_name=""):
        """Save successful prompt to CSV file with today's date"""
        try:
            # Get today's date in YY-MM-DD format
            today = datetime.now().strftime("%y-%m-%d")
            csv_filename = f"{today}.csv"
            
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(csv_filename)
            
            # Open CSV file in append mode
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'video_name', 'prompt', 'method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write the successful prompt
                writer.writerow({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'video_name': video_name,
                    'prompt': prompt,
                    'method': method_used
                })
            
            print(f"✓ Saved successful prompt to {csv_filename}")
            
        except Exception as e:
            print(f"⚠ Could not save prompt to CSV: {e}")
    
    def go_back_to_imagine_tab(self, go_back_twice=False):
        """Go back to imagine tab using browser back button"""
        try:
            current_url = self.driver.current_url
            if go_back_twice:
                print(f"\n🔙 Going back twice to imagine tab...")
            else:
                print(f"\n🔙 Going back to imagine tab...")
            print(f"  Current URL: {current_url}")
            
            # Use browser back button
            self.driver.back()
            time.sleep(2)  # Wait for page to load
            
            # If we used photo method, go back once more
            if go_back_twice:
                print("  Going back once more...")
                self.driver.back()
                time.sleep(2)
            
            # Wait for URL to change back to imagine tab
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: "imagine" in d.current_url.lower() or "grok.com" in d.current_url.lower()
                )
                print("✓ Back on imagine tab!")
                time.sleep(1)  # Give page time to fully load
            except:
                # If URL doesn't change, check if we're already there
                new_url = self.driver.current_url
                if "imagine" in new_url.lower():
                    print("✓ Already on imagine tab!")
                else:
                    print(f"⚠ URL after back: {new_url}")
                    print("  May need to navigate manually to imagine tab")
                    
        except Exception as e:
            print(f"⚠ Could not go back: {e}")
            print("  You may need to manually navigate back to imagine tab")
    
    def take_screenshot(self, filename):
        """Take a screenshot for debugging"""
        try:
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
        except:
            pass
    
    def close(self):
        """Disconnect from browser (doesn't close it!)"""
        if self.driver:
            try:
                print("\n✓ Disconnecting from browser (your Chrome stays open)")
                self.driver.quit()
            except:
                pass


def load_prompts_from_file(prompts_file="prompts.txt"):
    """Load prompts from a text file (one prompt per line)"""
    prompts = []
    
    if os.path.exists(prompts_file):
        # Try multiple encodings to handle different file encodings
        encodings = ['utf-8', 'utf-8-sig', 'cp949', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(prompts_file, 'r', encoding=encoding) as f:
                    for line in f:
                        # Strip whitespace and skip empty lines and comments
                        line = line.strip()
                        if line and not line.startswith('#'):
                            prompts.append(line)
                
                if prompts:
                    print(f"✓ Loaded {len(prompts)} prompt(s) from {prompts_file} (encoding: {encoding})")
                    return prompts
                else:
                    print(f"⚠ No valid prompts found in {prompts_file}")
                    return []
            except UnicodeDecodeError:
                # Try next encoding
                continue
            except Exception as e:
                # For other errors, try next encoding
                continue
        
        # If all encodings failed
        print(f"⚠ Error reading {prompts_file}: Could not decode with any encoding")
        print(f"  Tried: {', '.join(encodings)}")
    else:
        # Create a sample prompts file
        sample_prompts = [
            "A serene sunset over mountains with birds flying",
            "A futuristic city with flying cars at night",
            "Ocean waves crashing on a beach at dawn"
        ]
        try:
            with open(prompts_file, 'w', encoding='utf-8') as f:
                f.write("# Grok Video Generation Prompts\n")
                f.write("# One prompt per line\n")
                f.write("# Lines starting with # are ignored\n")
                f.write("# Empty lines are ignored\n\n")
                for prompt in sample_prompts:
                    f.write(f"{prompt}\n")
            print(f"✓ Created sample prompts file: {prompts_file}")
            print(f"  Please edit {prompts_file} with your prompts (one per line)")
            return sample_prompts
        except Exception as e:
            print(f"⚠ Could not create {prompts_file}: {e}")
    
    return prompts

def load_config(config_file="config.json"):
    """Load configuration from file (without prompts - prompts come from prompts.txt)"""
    default_config = {
        "use_existing_browser": True,
        "debugger_port": 9222,
        "video_wait_time": 180,
        "wait_between_videos": 10
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✓ Loaded config from {config_file}")
            # Remove prompts from config if present (we use prompts.txt now)
            if "prompts" in config:
                del config["prompts"]
            return {**default_config, **config}
        except:
            pass
    
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    print(f"✓ Created default config: {config_file}")
    
    return default_config


def create_chrome_shortcut_helper():
    """Helper to create a Chrome shortcut with debugging enabled"""
    print("\n" + "="*60)
    print("CREATE A CHROME SHORTCUT FOR AUTOMATION")
    print("="*60)
    print("\nOption 1: Use Batch File (RECOMMENDED)")
    print("-" * 60)
    batch_file = "start_chrome_debug.bat"
    if not os.path.exists(batch_file):
        automation = GrokVideoAutomation()
        automation.create_batch_file(batch_file)
        print(f"✓ Created '{batch_file}'")
    else:
        print(f"✓ '{batch_file}' already exists")
    print(f"  Double-click '{batch_file}' to start Chrome for automation")
    
    print("\nOption 2: Create Desktop Shortcut")
    print("-" * 60)
    print("1. Right-click on Desktop → New → Shortcut")
    print('2. Enter this as location:')
    print('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\ChromeDebug"')
    print('3. Name it "Chrome for Automation"')
    print('4. Double-click to launch')
    
    print("\n" + "="*60 + "\n")


def main():
    """Main function"""
    
    print("\n" + "="*60)
    print("Grok Video Automation (Existing Browser Mode)")
    print("="*60 + "\n")
    
    config = load_config()
    
    # Load prompts from text file
    # search for the file starts with "prompts_{today} ..." and ends with ".txt"
    today = datetime.now().strftime("%y-%m-%d")
    prompts_pattern = f"prompts_{today}_*.txt"
    matching_files = glob.glob(prompts_pattern)
    
    if matching_files:
        prompts_file = matching_files[0]
        print(f"Loading prompts from: {prompts_file}")
        prompts = load_prompts_from_file(prompts_file)
    else:
        # Fallback to default prompts.txt
        print("No date-specific prompts file found, trying prompts.txt...")
        prompts = load_prompts_from_file("prompts.txt")
    
    if not prompts:
        print("\n✗ No prompts found! Please add prompts to prompts.txt file")
        print("  One prompt per line in prompts.txt")
        return
    
    # Show setup instructions
    if config.get("use_existing_browser"):
        print("📌 SETUP INSTRUCTIONS:")
        print("="*60)
        print("1. Run: start_chrome_debug.bat (to start Chrome with debugging)")
        print("2. In that Chrome window, manually open: https://grok.com")
        print("3. Login to Grok if needed")
        print("4. Navigate to the 'Imagine' tab")
        print("5. Make sure you can see the input textarea")
        print("6. Then run this script to automate video creation")
        print("="*60 + "\n")
    
    automation = GrokVideoAutomation(
        use_existing_browser=config.get("use_existing_browser", True),
        debugger_port=config.get("debugger_port", 9222)
    )
    
    try:
        automation.start_browser()
        
        if not automation.navigate_to_grok():
            print("\n✗ Not logged in. Please login and try again.")
            automation.close()
            return
        
        # Generate videos
        successful = 0
        failed = 0
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{'='*60}")
            print(f"Video {i}/{len(prompts)}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            success = automation.generate_video(
                prompt, 
                wait_time=config["video_wait_time"]
            )
            
            if success:
                successful += 1
            else:
                failed += 1
            
            if i < len(prompts):
                wait = config['wait_between_videos']
                print(f"\n⏸ Waiting {wait} seconds...")
                time.sleep(wait)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print(f"📊 Total: {len(prompts)}")
        print("="*60 + "\n")
        
        input("\nPress Enter to disconnect (Chrome stays open)...")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        
        # Show setup helper if connection failed
        if "connection refused" in str(e).lower() or "cannot connect" in str(e).lower():
            create_chrome_shortcut_helper()
    finally:
        automation.close()


if __name__ == "__main__":
    main()