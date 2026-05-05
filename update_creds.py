import os, glob, re

path = r'c:\Users\yonas\Documents\qa-automacion-karrot'
files = glob.glob(os.path.join(path, 'TC*.py'))
pattern = re.compile(r'from_json_keyfile_name\(\s*r?[\'\"].*?\.json[\'\"]\s*,', re.DOTALL)
replacement = r'from_json_keyfile_name(r"C:\Users\yonas\Documents\qa-automacion-karrot\automatizacion-karrot-11b5a5de79c5.json",'

count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'automatizacion-karrot-11b5a5de79c5.json' not in content and 'from_json_keyfile_name' in content:
        # Use lambda in sub to perfectly insert text without resolving any backslashes like \U!
        new_content = pattern.sub(lambda m: replacement, content)
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            count += 1
            print(f'Updated {os.path.basename(f)}')

print(f'Total updated: {count}')
