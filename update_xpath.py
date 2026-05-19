import os
import glob

target_xpath = "\"//*[@id='root']/div/div/div/div[2]/div[2]/button\""
old_xpath_1 = "\"//button[contains(normalize-space(.), 'Ir al panel de administración')]\""
old_xpath_2 = "'//button[contains(normalize-space(.), \\'Ir al panel de administración\\')]'"
old_xpath_3 = "\"//button[contains(normalize-space(.), \\\"Ir al panel de administración\\\")]\""

count = 0
for filepath in glob.glob("TC*.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if old_xpath_1 in content or old_xpath_2 in content or old_xpath_3 in content:
        content = content.replace(old_xpath_1, target_xpath)
        content = content.replace(old_xpath_2, target_xpath)
        content = content.replace(old_xpath_3, target_xpath)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1
        print(f"Updated {filepath}")

print(f"Total files updated: {count}")
