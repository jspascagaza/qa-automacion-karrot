import os
import glob
import re

path = r'c:\Users\yonas\Documents'
files = glob.glob(os.path.join(path, 'TC*.py'))

# Pattern to find the current from_json_keyfile_name line
pattern = re.compile(r'from_json_keyfile_name\(\s*(.*?)\s*,\s*(scope|\[.*?\])\s*\)', re.DOTALL)

def replacer(match):
    return f'from_json_keyfile_name(r"C:\\Users\\yonas\\Documents\\automatizacion-karrot-456d1a1552ca.json", {match.group(2)})'

count = 0
for f in files:
    basename = os.path.basename(f)
    if not basename.startswith('TC'):
        continue

    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = pattern.sub(replacer, content)
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        count += 1
        print(f'Updated {basename}')
    else:
        # Fallback pattern for files like TC027 that use dotenv
        pattern2 = re.compile(r'from_json_keyfile_name\([\s\S]*?,\s*scope\s*\)', re.DOTALL)
        new_content2 = pattern2.sub(r'from_json_keyfile_name(r"C:\Users\yonas\Documents\automatizacion-karrot-456d1a1552ca.json", scope)', content)
        if new_content2 != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content2)
            count += 1
            print(f'Updated {basename} (fallback pattern)')

print(f'Total updated: {count}')
