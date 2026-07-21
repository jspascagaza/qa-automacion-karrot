import os
import glob
import ast

directory = "c:/Users/yonas/Documents"
all_py_files = glob.glob(os.path.join(directory, "*.py"))

count_fixed = 0
for filepath in all_py_files:
    if not os.path.exists(filepath):
        continue
        
    if "remove_" in filepath or "fix_" in filepath or "delete_" in filepath:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    try:
        ast.parse(content)
    except SyntaxError as e:
        # We likely have a stray ")"
        print(f"Syntax error in {filepath}: {e}")
        
        # Let's just remove any line that is EXACTLY just whitespace and ")"
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() == ")":
                continue
            new_lines.append(line)
            
        new_content = '\n'.join(new_lines)
        
        try:
            ast.parse(new_content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"-> Fixed syntax error in {filepath} by removing stray ')'")
            count_fixed += 1
        except SyntaxError as e2:
            print(f"-> Still has syntax error: {e2}")

print(f"Total files fixed for stray parenthesis: {count_fixed}")
