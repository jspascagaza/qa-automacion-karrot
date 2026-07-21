import os
import glob

directory = "c:/Users/yonas/Documents"
all_py_files = glob.glob(os.path.join(directory, "*.py"))

# The exact strings or patterns that we WANT to physically delete.
targets_to_delete = [
    "panel_button = wait.until",
    "panel_button = self.wait.until",
    "panel_button = WebDriverWait",
    "EC.element_to_be_clickable((By.XPATH, \"//button[contains(., 'administración')",
    "panel_button.click()",
    "print(\"✅ Click en 'Ir al panel de administración'\")",
    "wait.until(EC.url_contains(\"/app\"))",
    "self.wait.until(EC.url_contains(\"/app\"))",
    "WebDriverWait(self.driver, 5).until(EC.url_contains(\"/app\"))",
    "EC.url_contains(\"/app\")",
    "print(\"✅ Panel de control cargado",
    "print(\"🚀 Yendo al panel",
    "print(\"🚀 Intentando ir al panel",
    "except TimeoutException:",
    "print(\"ℹ️ Botón 'Ir al panel",
    "pass",
    "IR AL PANEL DE ADMINISTRACIÓN",
    "IR AL PANEL DE ADMINISTRACION REMOVIDO"
]

def should_delete(line):
    for target in targets_to_delete:
        if target in line:
            return True
    return False

count_fixed = 0
for filepath in all_py_files:
    if not os.path.exists(filepath):
        continue
        
    if "remove_" in filepath or "fix_" in filepath or "delete_" in filepath:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
        
    new_lines = []
    modified = False
    
    for line in lines:
        if line.startswith('# '):
            # The original line without the "# " that we prepended
            original = line[2:]
            
            # If the original line is one of our targets, we DELETE it (by not appending anything)
            if should_delete(original):
                modified = True
                continue
                
            # If the original line is actually a time.sleep that was part of the target block
            if original.strip() == "time.sleep(5)":
                modified = True
                continue
                
            # Otherwise, this is a VALID line of code that we mistakenly commented out!
            # We MUST restore it by appending the original line.
            # (We only do this for lines that have indentation, because our script only messed up inside functions)
            if original.startswith(' ') or original.startswith('\t') or original == '':
                new_lines.append(original)
                modified = True
                continue
                
        # For lines that don't start with '# ', or if they do but don't match our criteria,
        # we check if they are target lines (in case they weren't commented out)
        if should_delete(line):
            modified = True
            continue
            
        if line.strip() == "time.sleep(5)" and len(new_lines) > 0 and "url_contains(\"/app\")" in new_lines[-1]:
             modified = True
             continue
             
        new_lines.append(line)
        
    if modified:
        # Clean up empty lines
        new_content = '\n'.join(new_lines)
        import re
        new_content = re.sub(r'\n[ \t]*\n[ \t]*\n', '\n\n', new_content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed and cleaned {filepath}")
        count_fixed += 1

print(f"Total files fixed: {count_fixed}")
