import os
import re

dir_path = r"c:\Users\yonas\Documents"

for filename in os.listdir(dir_path):
    if filename.endswith(".py"):
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace EC.presence_of_element_located for Panel de control with a check for URL contains '/app'
        # Original: wait.until(EC.url_contains("/app"))
        new_content = re.sub(
            r'wait\.until\(EC\.presence_of_element_located\(\(By\.XPATH,\s*"//h2\[contains\(text\(\),\s*\'Panel de control\'\)\]"\)\)\)',
            r'wait.until(EC.url_contains("/app"))',
            content
        )
        
        # also handle cases where it spans multiple lines or has slightly different quotes
        new_content = re.sub(
            r'EC\.presence_of_element_located\(\(By\.XPATH,\s*[\'"]//h2\[contains\(text\(\),\s*\'Panel de control\'\)\][\'"]\)\)',
            r'EC.url_contains("/app")',
            new_content
        )

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filename}")
