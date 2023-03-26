import subprocess

def find_top_level_variable(file_path, line_number):
    result = subprocess.run(
        ["node", "find_variable.js", file_path, str(line_number)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

code_file_path = "../picnic/packages/app/frontend/modules/pdf_annotator/actions.ts"
line_number = 860

top_level_variable = find_top_level_variable(code_file_path, line_number)
print(top_level_variable)

