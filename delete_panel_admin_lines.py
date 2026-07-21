import os
import glob

directory = "c:/Users/yonas/Documents"
all_py_files = glob.glob(os.path.join(directory, "*.py"))

lines_to_delete = [
    "IR AL PANEL DE ADMINISTRACIÓN",
    "IR AL PANEL DE ADMINISTRACION REMOVIDO",
    "panel_button = wait.until",
    "panel_button = self.wait.until",
    "panel_button = WebDriverWait",
    "EC.element_to_be_clickable((By.XPATH, \"//button[contains(., 'administración')",
    "panel_button.click()",
    "print(\"✅ Click en 'Ir al panel de administración'\")",
    "wait.until(EC.url_contains(\"/app\"))",
    "self.wait.until(EC.url_contains(\"/app\"))",
    "WebDriverWait(self.driver, 5).until(EC.url_contains(\"/app\"))",
    "print(\"✅ Panel de control cargado",
    "print(\"🚀 Yendo al panel",
    "print(\"🚀 Intentando ir al panel",
    "except TimeoutException:",
    "print(\"ℹ️ Botón 'Ir al panel",
    "pass"
]

count_modified = 0
for filepath in all_py_files:
    if not os.path.exists(filepath):
        continue
    
    # Don't modify our script files
    if "remove_panel" in filepath or "delete_panel" in filepath:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file has any of the commented out lines we added
    if '# ' not in content and 'panel_button' not in content:
        continue
        
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # If the line is empty, keep it unless we are trying to clean up spaces? Keep it for safety.
        
        # Check if the line is one of the commented out ones we want to delete
        should_delete = False
        if stripped.startswith('#'):
            for target in lines_to_delete:
                if target in stripped:
                    should_delete = True
                    break
                    
            # Special case for the "time.sleep(5)" that followed the panel load
            # We commented it out, so it looks like "# time.sleep(5)" or "#             time.sleep(5)"
            if stripped == '# time.sleep(5)' or stripped == '# time.sleep(15)' or stripped == '# time.sleep(10)':
                # Actually, only delete it if it's the specific one we commented out for the panel
                if "time.sleep" in stripped:
                    should_delete = True
        
        if not should_delete:
            new_lines.append(line)
            
    new_content = '\n'.join(new_lines)
    
    # Clean up multiple consecutive empty lines created by deletion
    import re
    new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned up {filepath}")
        count_modified += 1

print(f"Total cleaned files: {count_modified}")
