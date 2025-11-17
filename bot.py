from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import string
import time
import os
import sys

class RailwayTalbersCreator:
    def __init__(self):
        self.created_accounts = []
        self.success_count = 0
        self.fail_count = 0
        self.driver = None
        
    def setup_driver(self):
        """إعداد متصفح متوافق مع Railway"""
        chrome_options = Options()
        
        # إعدادات لـ Railway
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        # تجنب الكشف كبوت
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # لمشاكل Chrome في Railway
            chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN', 'chromium')
            self.driver = webdriver.Chrome(
                executable_path=os.environ.get('CHROMEDRIVER_PATH', 'chromedriver'),
                options=chrome_options
            )
        except:
            # استخدام السواقة الافتراضية
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(15)
        return self.driver
    
    def generate_random_email(self):
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def generate_random_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def fill_form_quickly(self, driver, email, password):
        """ملء النموذج بسرعة وبكفاءة"""
        try:
            # الحصول على جميع الحقول مرة واحدة
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            
            if len(all_inputs) < 3:
                return False
            
            # ملء الحقول بالتسلسل
            inputs_to_fill = [
                (0, email),      # البريد الإلكتروني
                (1, password),   # كلمة المرور الأولى
                (2, password),   # تأكيد كلمة المرور
            ]
            
            for index, value in inputs_to_fill:
                if index < len(all_inputs):
                    all_inputs[index].clear()
                    all_inputs[index].send_keys(value)
                    time.sleep(0.5)  # انتظار قصير بين الحقول
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في ملء النموذج: {e}")
            return False
    
    def click_signup_smart(self, driver):
        """نقر ذكي على زر التسجيل"""
        try:
            # المحاولة الأولى: البحث عن روابط Sign Up
            signup_links = driver.find_elements(By.XPATH, "//a[contains(., 'Sign Up')]")
            if signup_links:
                driver.execute_script("arguments[0].click();", signup_links[0])
                return True
            
            # المحاولة الثانية: البحث عن أزرار
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Sign Up" in button.text or "Sign up" in button.text:
                    driver.execute_script("arguments[0].click();", button)
                    return True
            
            # المحاولة الثالثة: أي زر submit
            submit_buttons = driver.find_elements(By.XPATH, "//button[@type='submit']")
            if submit_buttons:
                driver.execute_script("arguments[0].click();", submit_buttons[0])
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ خطأ في النقر: {e}")
            return False
    
    def create_account_batch(self, start_number, batch_size=10):
        """إنشاء مجموعة من الحسابات"""
        batch_results = []
        
        for i in range(start_number, start_number + batch_size):
            try:
                print(f"🎯 إنشاء الحساب #{i}")
                
                # زيارة صفحة التسجيل
                self.driver.get("https://talbers.com/#/register?ref=544726")
                time.sleep(3)
                
                # توليد البيانات
                email = self.generate_random_email()
                password = self.generate_random_password()
                
                # ملء النموذج
                if not self.fill_form_quickly(self.driver, email, password):
                    print(f"❌ فشل في ملء النموذج للحساب #{i}")
                    self.fail_count += 1
                    continue
                
                # النقر على التسجيل
                if not self.click_signup_smart(self.driver):
                    print(f"❌ فشل في النقر للحساب #{i}")
                    self.fail_count += 1
                    continue
                
                # انتظار النتيجة
                time.sleep(4)
                
                # التحقق من النجاح
                current_url = self.driver.current_url
                status = "success" if "register" not in current_url else "unknown"
                
                account_info = {
                    'email': email,
                    'password': password,
                    'status': status,
                    'account_number': i
                }
                
                batch_results.append(account_info)
                self.created_accounts.append(account_info)
                
                if status == "success":
                    self.success_count += 1
                    print(f"✅ تم إنشاء الحساب #{i}: {email}")
                else:
                    self.fail_count += 1
                    print(f"⚠️ حالة غير مؤكدة للحساب #{i}")
                
                # انتظار 3 ثواني قبل الحساب التالي
                if i < start_number + batch_size - 1:
                    time.sleep(3)
                    
            except Exception as e:
                print(f"💥 خطأ غير متوقع للحساب #{i}: {e}")
                self.fail_count += 1
                continue
        
        return batch_results
    
    def run_mass_creation(self, total_accounts=500, batch_size=20):
        """تشغيل الإنشاء الجماعي"""
        print(f"🚀 بدء إنشاء {total_accounts} حساب على Railway")
        print("⚡ المطور: Sαταи")
        print("🌐 جاري إعداد المتصفح...")
        
        # إعداد المتصفح مرة واحدة
        self.setup_driver()
        
        start_time = time.time()
        accounts_created = 0
        
        try:
            while accounts_created < total_accounts:
                remaining = total_accounts - accounts_created
                current_batch_size = min(batch_size, remaining)
                
                print(f"\n📦 الدفعة التالية: {current_batch_size} حساب")
                print(f"📊 الإجمالي حتى الآن: {self.success_count} ناجح | {self.fail_count} فاشل")
                
                batch_results = self.create_account_batch(
                    accounts_created + 1, 
                    current_batch_size
                )
                
                accounts_created += current_batch_size
                
                # حفظ تقدم كل 50 حساب
                if accounts_created % 50 == 0:
                    self.save_progress()
                    print(f"💾 تم حفظ التقدم عند {accounts_created} حساب")
                
                # تقرير كل دفعة
                batch_success = len([acc for acc in batch_results if acc['status'] == 'success'])
                print(f"✅ الدفعة: {batch_success}/{current_batch_size} ناجح")
                
                # استراحة قصيرة بين الدفعات
                if accounts_created < total_accounts:
                    print("⏳ استراحة 10 ثواني قبل الدفعة التالية...")
                    time.sleep(10)
        
        except KeyboardInterrupt:
            print("\n⏹️ تم إيقاف العملية بواسطة المستخدم")
        except Exception as e:
            print(f"💥 خطأ رئيسي: {e}")
        finally:
            # إغلاق المتصفح
            if self.driver:
                self.driver.quit()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # التقرير النهائي
            self.generate_final_report(duration)
    
    def save_progress(self):
        """حفظ التقدم الحالي"""
        filename = f"talbers_progress_{int(time.time())}.json"
        progress_data = {
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'created_accounts': self.created_accounts,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def generate_final_report(self, duration):
        """تقرير نهائي مفصل"""
        print(f"\n{'='*70}")
        print("📊 التقرير النهائي - إنشاء حسابات Talbers")
        print(f"{'='*70}")
        print(f"🎯 المطور: Sαταи")
        print(f"⏱️ الوقت المستغرق: {duration:.2f} ثانية ({duration/60:.2f} دقيقة)")
        print(f"✅ الحسابات الناجحة: {self.success_count}")
        print(f"❌ الحسابات الفاشلة: {self.fail_count}")
        print(f"📈 معدل النجاح: {(self.success_count/(self.success_count + self.fail_count))*100:.1f}%")
        print(f"⚡ السرعة: {(self.success_count + self.fail_count)/(duration/60):.1f} حساب/دقيقة")
        
        # حفظ النتائج النهائية
        self.save_final_results()
        
        # عرض عينة من الحسابات
        if self.created_accounts:
            print(f"\n📧 عينة من الحسابات المخلوقة:")
            for i, account in enumerate(self.created_accounts[:10]):
                status_icon = "✅" if account['status'] == 'success' else "⚠️"
                print(f"{status_icon} {account['email']} | {account['password']}")
    
    def save_final_results(self):
        """حفظ النتائج النهائية في ملف"""
        filename = f"talbers_500_accounts_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("نتائج إنشاء 500 حساب Talbers - الإصدار النهائي\n")
                f.write("=" * 60 + "\n")
                f.write(f"المطور: Sαταи\n")
                f.write(f"الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"إجمالي المحاولات: {len(self.created_accounts)}\n")
                f.write(f"ناجحة: {self.success_count} | فاشلة: {self.fail_count}\n\n")
                
                for account in self.created_accounts:
                    status_icon = "✅" if account['status'] == 'success' else "⚠️"
                    f.write(f"{status_icon} الحساب #{account['account_number']}\n")
                    f.write(f"   📧 {account['email']}\n")
                    f.write(f"   🔑 {account['password']}\n")
                    f.write(f"   📊 {account['status']}\n")
                    f.write("-" * 50 + "\n")
            
            print(f"💾 تم حفظ النتائج في: {filename}")
        except Exception as e:
            print(f"❌ خطأ في حفظ الملف: {e}")

# ملف requirements.txt للـ Railway
"""
selenium==4.15.0
webdriver-manager==4.0.1
"""

# ملف Railway.toml مثال
"""
[build]
builder = "heroku/buildpacks:20"

[build.environment]
NODE_VERSION = "18"

[env]
CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
GOOGLE_CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
"""

if __name__ == "__main__":
    print("🔥 إصدار Railway - إنشاء 500 حساب Talbers")
    print("⚡ جاري البدء...")
    
    # التحقق من وجود المتصفح
    try:
        creator = RailwayTalbersCreator()
        creator.run_mass_creation(500, 25)  # 500 حساب، 25 في كل دفعة
    except Exception as e:
        print(f"💥 فشل في تشغيل الأداة: {e}")
        sys.exit(1)
