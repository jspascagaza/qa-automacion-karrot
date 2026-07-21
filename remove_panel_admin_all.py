import os
import re
import glob

directory = "c:/Users/yonas/Documents"
all_py_files = glob.glob(os.path.join(directory, "*.py"))

def comment_out_blocks(content):
    lines = content.split('\n')
    new_lines = []
    
    skip_mode = False
    skip_braces = 0
    
    for i, line in enumerate(lines):
        # Start of a panel_button assignment
        if re.search(r'panel_button\s*=\s*(self\.wait|wait|WebDriverWait)', line) and not line.strip().startswith('#'):
            skip_mode = True
            new_lines.append('# ' + line)
            if '(' in line:
                skip_braces += line.count('(') - line.count(')')
            continue
            
        if skip_mode:
            new_lines.append('# ' + line)
            skip_braces += line.count('(') - line.count(')')
            # If we balanced braces and also hit panel_button.click(), we might still be in skip mode for the next few lines.
            if skip_braces <= 0 and 'panel_button.click()' in line:
                skip_mode = "post_click"
            continue
            
        if skip_mode == "post_click":
            stripped = line.strip()
            # If it's a related line, comment it out
            if stripped == '' or \
               'print("✅ Click en \'Ir al panel' in line or \
#                'wait.until(EC.url_contains("/app"))' in line or \
               'WebDriverWait' in line and 'EC.url_contains("/app")' in line or \
               'EC.url_contains("/app")' in line or \
               'print("✅ Panel de control cargado' in line or \
               'print("🚀 Yendo al panel' in line or \
               'print("🚀 Intentando ir al panel' in line or \
               'time.sleep(5)' in line or \
               'except TimeoutException:' in line or \
               'print("ℹ️ Botón \'Ir al panel' in line:
                new_lines.append('# ' + line)
                continue
            else:
                skip_mode = False
                new_lines.append(line)
                continue
                
        # Also catch standalone URL waits if they missed the post_click
#         if not line.strip().startswith('#') and 'wait.until(EC.url_contains("/app"))' in line:
            new_lines.append('# ' + line)
            continue
            
        new_lines.append(line)
        
    return '\n'.join(new_lines)

count_modified = 0
for filepath in all_py_files:
    if not os.path.exists(filepath):
        continue
    
    # Don't modify the script itself
    if "remove_panel_admin.py" in filepath:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = comment_out_blocks(content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Modified {filepath}")
        count_modified += 1

print(f"Total modified files: {count_modified}")
