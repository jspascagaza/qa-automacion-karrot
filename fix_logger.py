import glob

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the write method
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
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
