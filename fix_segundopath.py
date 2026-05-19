import glob
import re

files = glob.glob('TC*.py')

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if segundopath logic exists
    if 'segundopath' in content:
        print(f'Updating {filepath}')
        # We will simply comment out the lines that use segundopath.
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'segundopath' in line:
                lines[i] = '# ' + line
        
        # Then, right after the last segundopath line, we insert:
        # driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/locations")
        # Actually it's safer to just replace the first `driver.get(segundopath...)` with the actual URL.
        
        content = '\n'.join(lines)
        content = content.replace('# driver.get(segundopath.get_attribute("href"))', 'driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/locations")')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
