import glob

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('print("⏳ Navegando a "rdenes de Compra...")', 'print("⏳ Navegando a Ordenes de Compra...")')
    content = content.replace('EXTRACCI"N', 'EXTRACCION')
    content = content.replace('"RDENES', 'ORDENES')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
