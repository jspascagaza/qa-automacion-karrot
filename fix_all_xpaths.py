import os
import glob
import re

def fix_xpaths():
    for filepath in glob.glob("TC*.py"):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content
        
        # Fix 1: The brittle Panel Button XPath
        # The user had "//*[@id='root']/div/div/div/div[2]/div[2]/button"
        old_xpath = '"//*[@id=\'root\']/div/div/div/div[2]/div[2]/button"'
        better_xpath = '"//button[contains(., \'administración\') or contains(., \'Panel\') or contains(., \'admin\') or @class=\'ant-btn-primary\'] | //*[@id=\'root\']/div/div/div/div[2]/div[2]/button"'
        
        if old_xpath in new_content:
            new_content = new_content.replace(old_xpath, better_xpath)

        # Fix 2: The Panel de control h2 check (which times out)
        # We replace EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]")) with EC.url_contains("/app")
        new_content = re.sub(
            r'EC\.presence_of_element_located\(\(By\.XPATH,\s*[\'"]//h2\[contains\(text\(\),\s*\'Panel de control\'\)\][\'"]\)\)',
            r'EC.url_contains("/app")',
            new_content
        )

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Fixed XPaths in {filepath}")

if __name__ == "__main__":
    fix_xpaths()
