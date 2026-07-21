import os
import re
import glob

def main():
    test_files = glob.glob("TC*.py")
    
    for filepath in test_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content
        
        # Fix 1: first_name[0]
        new_content = re.sub(
            r'user\s*=\s*\(first_name\[0\]\s*\+\s*last_name\)\.lower\(\)\.replace\(" ",\s*""\)',
            r'user = ((first_name[0] if first_name else "") + (last_name if last_name else "")).lower().replace(" ", "")',
            new_content
        )

        # Fix 2: Faker.address() -> Faker().address() 
        # But maybe they already imported faker correctly. Let's see if Faker() works.
        # Often it's `fake = Faker()` or similar. If they just did `Faker.address()`, it's an error.
        new_content = re.sub(
            r'Faker\.address\(\)',
            r'Faker().address()',
            new_content
        )
        
        # Fix 3: Unicode encode error on stdout logger
        # Replace: self.terminal.write(message)
        # With:
        # try:
        #     self.terminal.write(message)
        # except UnicodeEncodeError:
        #     self.terminal.write(message.encode('cp1252', 'ignore').decode('cp1252'))
        
        logger_fix = """        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('cp1252', 'ignore').decode('cp1252'))"""
            
        new_content = new_content.replace("        self.terminal.write(message)", logger_fix)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Fixed {filepath}")

if __name__ == '__main__':
    main()
