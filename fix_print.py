import glob

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")', 'print(f"CRITICAL ERROR: {str(e)}"); registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
