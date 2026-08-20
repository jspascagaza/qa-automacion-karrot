import glob

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('                print("o. Lugar de Entrega seleccionado correctamente.")\n        time.sleep(1)', '        print("o. Lugar de Entrega seleccionado correctamente.")\n        time.sleep(1)')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
