import glob
import re

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the indentation error
    content = content.replace("            input_proveedor.send_keys(proveedor_nombre)\n            time.sleep(2)", "            input_proveedor.send_keys(proveedor_nombre)\n            time.sleep(2)")
    # Wait, the code_to_insert had:
    # """            input_proveedor.send_keys(proveedor_nombre)
    #         time.sleep(2)
    # ..."""
    # which actually matches the 12-space indentation. Why was it an IndentationError?
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'input_proveedor.send_keys(proveedor_nombre)' in line:
            # Let's just fix it by ensuring it matches the previous line's indent
            # Or just normalize it.
            pass
