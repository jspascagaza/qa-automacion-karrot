import os
import glob
import subprocess
import re

directory = "c:/Users/yonas/Documents"
all_py_files = glob.glob(os.path.join(directory, "*.py"))

def get_unmatched_paren_line(filepath):
    result = subprocess.run(['python', '-m', 'py_compile', filepath], capture_output=True, text=True)
    if result.returncode != 0:
        # Looking for:
        # File "...", line 751
        #     )
        #     ^
        # SyntaxError: unmatched ')'
        if "unmatched ')'" in result.stderr:
            match = re.search(r'line (\d+)', result.stderr)
            if match:
                return int(match.group(1))
    return None

count_fixed = 0
for filepath in all_py_files:
    if not os.path.exists(filepath):
        continue
        
    if "remove_" in filepath or "fix_" in filepath or "delete_" in filepath:
        continue
        
    while True:
        line_num = get_unmatched_paren_line(filepath)
        if line_num is None:
            break
            
        # We found an unmatched ')' at line_num. Let's delete it.
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
            
        # line_num is 1-indexed
        target_idx = line_num - 1
        
        # Verify it's actually just a closing paren
        if lines[target_idx].strip() == ')':
            print(f"Removing stray ')' at line {line_num} in {filepath}")
            del lines[target_idx]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            count_fixed += 1
        else:
            print(f"WARNING: Line {line_num} in {filepath} has unmatched ')' but is not just ')': {lines[target_idx]}")
            break

print(f"Total stray parenthesis removed: {count_fixed}")
