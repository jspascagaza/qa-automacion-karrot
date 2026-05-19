import os
import re
import glob

def update_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        file_encoding = 'utf-8'
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-16') as f:
            content = f.read()
        file_encoding = 'utf-16'

    # Skip if it doesn't contain login-form_email
    if 'login-form_email' not in content:
        return False

    original_content = content

    # Add dotenv import if not present
    if 'from dotenv import load_dotenv' not in content:
        # Insert after the first import or at the beginning
        import_stmt = "import os\nfrom dotenv import load_dotenv\nload_dotenv()\n"
        if "import " in content:
            content = re.sub(r'^(.*?import [^\n]+)', r'\1\n' + import_stmt, content, count=1, flags=re.MULTILINE|re.DOTALL)
        else:
            content = import_stmt + "\n" + content

    # Replace email send_keys. Look for email_input.send_keys("...") or similar
    # Sometimes it's email_input.send_keys(os.getenv(...)) already.
    # Let's match: email_input.send_keys("something") or ('something')
    
    # We can match any send_keys after login-form_email, but it's safer to specifically look for
    # email_input.send_keys(...)
    
    content = re.sub(
        r'(email_input\.send_keys\()\s*["\'][^"\']*["\']\s*\)',
        r'\1os.getenv("KARROT_LOGIN_EMAIL", "karrotdev@outlook.com"))',
        content
    )
    # Also replace if it was already os.getenv("KARROT_USER"...)
    content = re.sub(
        r'os\.getenv\(\s*["\']KARROT_USER["\'][^)]*\)',
        r'os.getenv("KARROT_LOGIN_EMAIL", "karrotdev@outlook.com")',
        content
    )

    # Replace password send_keys
    content = re.sub(
        r'(password_input\.send_keys\()\s*["\'][^"\']*["\']\s*\)',
        r'\1os.getenv("KARROT_LOGIN_PASSWORD", "P4sc4g4z42025#*"))',
        content
    )
    # Also replace if it was already os.getenv("KARROT_PASSWORD"...)
    content = re.sub(
        r'os\.getenv\(\s*["\']KARROT_PASSWORD["\'][^)]*\)',
        r'os.getenv("KARROT_LOGIN_PASSWORD", "P4sc4g4z42025#*")',
        content
    )

    if content != original_content:
        with open(filepath, 'w', encoding=file_encoding) as f:
            f.write(content)
        return True
    return False

if __name__ == '__main__':
    py_files = glob.glob('*.py')
    updated = 0
    for f in py_files:
        # Skip self or other utility scripts if needed, though they don't have login-form_email
        if f == 'update_login_creds.py': continue
        if update_file(f):
            print(f"Updated: {f}")
            updated += 1
    print(f"Total files updated: {updated}")
