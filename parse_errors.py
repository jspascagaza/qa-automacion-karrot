import re

def parse_logs():
    with open('logs jenkins.txt', 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    # The log might not be split by ====, it might just be sequential output.
    # Let's search for "Traceback" or "Exception" and backtrack to find the test file.
    
    lines = data.split('\n')
    current_file = "Unknown"
    errors = {}
    
    for i, line in enumerate(lines):
        # Detect file being run
        m = re.search(r'(TC\d{3}.*?\.py)', line)
        if m:
            current_file = m.group(1)
            
        if 'Traceback (most recent call last):' in line or 'Exception:' in line or 'Error:' in line:
            if current_file not in errors:
                # Capture the next few lines for context
                context = '\n'.join(lines[i:i+10])
                errors[current_file] = context

    with open('errors_report.txt', 'w', encoding='utf-8') as out_f:
        for k, v in errors.items():
            out_f.write(f"--- {k} ---\n")
            out_f.write(v + "\n\n")

if __name__ == '__main__':
    parse_logs()
