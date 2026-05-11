import os
import glob
import re

path = r'c:\Users\yonas\Documents'
files = glob.glob(os.path.join(path, 'TC*.py'))

# Pattern for replacing the credential loading line
pattern = re.compile(r'from_json_keyfile_name\(\s*.*?\s*,\s*(scope|\[.*?\])\s*\)', re.DOTALL)
replacement_str = r'from_json_keyfile_name(\n    os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-456d1a1552ca.json"),\n    \1\n)'

count = 0
for f in files:
    basename = os.path.basename(f)
    if not basename.startswith('TC'):
        continue

    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if load_dotenv is present
    has_dotenv = 'load_dotenv()' in content
    
    new_content = pattern.sub(replacement_str, content)
    
    # If not present, inject imports right after ServiceAccountCredentials
    if not has_dotenv and 'ServiceAccountCredentials' in new_content:
        import_injection = "from oauth2client.service_account import ServiceAccountCredentials\nimport os\nfrom dotenv import load_dotenv\nload_dotenv()\n"
        new_content = new_content.replace(
            "from oauth2client.service_account import ServiceAccountCredentials",
            import_injection,
            1 # Only replace the first occurrence
        )
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        count += 1
        print(f'Updated {basename} (Added dotenv: {not has_dotenv})')

print(f'Total updated: {count}')
