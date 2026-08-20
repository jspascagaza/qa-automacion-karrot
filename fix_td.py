import glob

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Change td[1] to td[2] for the provider name extraction
    old_code = 'celda_nombre = driver.find_element(By.XPATH, "(//table/tbody/tr[contains(@class, \'ant-table-row\')])[1]/td[1]")'
    new_code = 'celda_nombre = driver.find_element(By.XPATH, "(//table/tbody/tr[contains(@class, \'ant-table-row\')])[1]/td[2]")'
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file}")
