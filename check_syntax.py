import os
import glob
import py_compile

directory = "c:/Users/yonas/Documents"
all_py_files = glob.glob(os.path.join(directory, "*.py"))

errors = 0
for f in all_py_files:
    if 'remove_' in f or 'fix_' in f or 'delete_' in f:
        continue
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        print(f"Error in {os.path.basename(f)}: {e}")
        errors += 1

print(f"Total files with errors: {errors}")
