import glob

code_to_replace = """                            texto_limpio = texto.split('
')[-1].strip()"""

code_to_insert = """                            texto_limpio = texto.split('\\n')[-1].strip()"""

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if code_to_replace in content:
        new_content = content.replace(code_to_replace, code_to_insert)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {file}')
    else:
        print(f'Not found in {file}')
