import glob

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the quotes typo
    content = content.replace('print("⏳ Navegando a "rdenes de Compra...")', 'print("⏳ Navegando a Ordenes de Compra...")')
    content = content.replace('EXTRACCI"N', 'EXTRACCION')
    content = content.replace('"RDENES', 'ORDENES')
    content = content.replace('Configuraci"n', 'Configuracion')
    content = content.replace('print("⏳ Navegando a "rdenes de Compra...")', 'print("Navegando a Ordenes de Compra...")')
    
    # Fix the logger
    old_write = """    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()"""
    
    new_write = """    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('ascii', 'ignore').decode('ascii'))
        self.log.write(message)
        self.log.flush()"""
    
    content = content.replace(old_write, new_write)
    
    # Also add print inside the exception handler
    content = content.replace('registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")', 'print(f"CRITICAL ERROR: {str(e)}"); registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
