#!/usr/bin/env python
"""
Script to fix specific linting errors in the Gitelle project.
This script addresses the exact errors from the CI output.
"""

import os
import re
from pathlib import Path

# List of specific errors to fix
ERRORS = [
    ("src/gitelle/commands/add.py", 51, "F541"),  # f-string missing placeholders
    ("src/gitelle/commands/branch.py", 46, "E501"),  # line too long
    ("src/gitelle/commands/branch.py", 48, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 19, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 27, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 28, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 44, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 54, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 55, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 76, "E501"),  # line too long
    ("src/gitelle/commands/clone.py", 78, "E501"),  # line too long
    ("src/gitelle/commands/commit.py", 44, "E501"),  # line too long
    ("src/gitelle/commands/diff.py", 158, "E501"),  # line too long
    ("src/gitelle/commands/init.py", 23, "E501"),  # line too long
    ("src/gitelle/commands/status.py", 138, "E501"),  # line too long
    ("src/gitelle/commands/status.py", 140, "E501"),  # line too long
    ("src/gitelle/commands/status.py", 147, "E501"),  # line too long
    ("src/gitelle/core/index.py", 205, "E501"),  # line too long
    ("src/gitelle/core/index.py", 229, "E501"),  # line too long
    ("src/gitelle/core/objects.py", 170, "F811"),  # redefinition of unused function
    ("src/gitelle/core/refs.py", 120, "E501"),  # line too long
    ("src/gitelle/core/refs.py", 123, "E501"),  # line too long
    ("src/gitelle/core/repository.py", 86, "E501"),  # line too long
    ("src/gitelle/core/repository.py", 203, "E501"),  # line too long
    ("src/gitelle/core/repository.py", 292, "E501"),  # line too long
    ("src/gitelle/core/repository.py", 323, "E501"),  # line too long
]

def fix_f_string_missing_placeholders(file_path, line_number):
    """Fix f-strings that are missing placeholders."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if 0 <= line_number - 1 < len(lines):
        line = lines[line_number - 1]
        
        # Look for f-strings without placeholders
        matches = re.finditer(r'f(["\'])(.*?)(\1)', line)
        for match in matches:
            # If the string doesn't contain '{', it's missing placeholders
            if '{' not in match.group(2):
                # Replace f-string with regular string
                before = line[:match.start()]
                after = line[match.end():]
                new_line = f"{before}{match.group(1)}{match.group(2)}{match.group(3)}{after}"
                lines[line_number - 1] = new_line
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed missing placeholders in {file_path}:{line_number}")

def fix_line_too_long(file_path, line_number):
    """Fix lines that are too long."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if 0 <= line_number - 1 < len(lines):
        line = lines[line_number - 1]
        
        # Skip if line is already okay
        if len(line.rstrip('\n')) <= 79:
            print(f"Line {line_number} in {file_path} is already <= 79 chars")
            return
        
        # Get indentation level
        indentation = len(line) - len(line.lstrip())
        indent = ' ' * indentation
        continuation_indent = ' ' * (indentation + 4)
        
        # Different strategies based on line content
        if '(' in line and ')' in line:
            # Function call or definition
            open_paren = line.find('(')
            close_paren = line.rfind(')')
            
            if open_paren > 0 and close_paren > open_paren:
                # Get content between parentheses
                prefix = line[:open_paren + 1]
                content = line[open_paren + 1:close_paren]
                suffix = line[close_paren:]
                
                # Split at commas
                if ',' in content:
                    parts = [p.strip() for p in content.split(',')]
                    
                    # Reconstruct the line with line breaks after commas
                    new_lines = [prefix]
                    current_line = ""
                    
                    for i, part in enumerate(parts):
                        delimiter = ',' if i < len(parts) - 1 else ''
                        if len(current_line + part + delimiter) <= 75 - len(prefix):
                            if current_line:
                                current_line += f"{part}{delimiter}"
                            else:
                                current_line = f"{part}{delimiter}"
                        else:
                            if current_line:
                                new_lines.append(current_line)
                            current_line = f"{continuation_indent}{part}{delimiter}"
                    
                    if current_line:
                        new_lines.append(current_line)
                    
                    new_lines.append(f"{indent}{suffix}")
                    
                    # Replace the original line with the new lines
                    lines[line_number - 1] = new_lines[0] + '\n'
                    for i in range(1, len(new_lines)):
                        lines.insert(line_number - 1 + i, new_lines[i] + '\n')
                else:
                    # Simple break after opening parenthesis
                    new_line = f"{prefix}\n{continuation_indent}{content.strip()}{suffix}"
                    lines[line_number - 1] = new_line
        
        elif '=' in line:
            # Assignment
            parts = line.split('=', 1)
            left = parts[0].rstrip()
            right = parts[1].lstrip()
            
            # Break after equals sign
            new_line = f"{left}=\n{continuation_indent}{right}"
            lines[line_number - 1] = new_line
        
        elif '"' in line or "'" in line:
            # String - split it
            str_match = re.search(r'(["\'])(.*?)(\1)', line)
            if str_match:
                before_str = line[:str_match.start()]
                string_content = str_match.group(2)
                after_str = line[str_match.end():]
                
                # Find a good breaking point in the string
                mid_point = len(string_content) // 2
                # Look for space near the middle
                space_pos = string_content.rfind(' ', 0, mid_point)
                if space_pos == -1:
                    space_pos = string_content.find(' ', mid_point)
                
                if space_pos != -1:
                    first_part = string_content[:space_pos]
                    second_part = string_content[space_pos:].lstrip()
                    
                    # Break the string into multiple strings with concatenation
                    new_line = f"{before_str}'{first_part}' +\n{continuation_indent}'{second_part}'{after_str}"
                    lines[line_number - 1] = new_line
        
        else:
            # Generic line breaking
            mid_point = 75  # Safe point to break
            good_break = -1
            
            # Try to find a good breaking character
            for char in [' ', ',', ';', ':', '+', '-', '*', '/', '&', '|']:
                pos = line.rfind(char, 0, mid_point)
                if pos > good_break:
                    good_break = pos
            
            if good_break > 0:
                # Break at the good breaking point
                first_part = line[:good_break + 1].rstrip()
                second_part = line[good_break + 1:].lstrip()
                
                if char == ' ':
                    new_line = f"{first_part}\\\n{continuation_indent}{second_part}"
                else:
                    new_line = f"{first_part}\n{continuation_indent}{second_part}"
                
                lines[line_number - 1] = new_line
            else:
                # Force break at the mid point
                first_part = line[:mid_point].rstrip()
                second_part = line[mid_point:].lstrip()
                new_line = f"{first_part}\\\n{continuation_indent}{second_part}"
                lines[line_number - 1] = new_line
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed long line in {file_path}:{line_number}")

def fix_redefined_function(file_path, line_number):
    """Fix redefined function."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if 0 <= line_number - 1 < len(lines):
        line = lines[line_number - 1]
        
        # Comment out the redefined function
        lines[line_number - 1] = f"# {line}"
        
        # Find the function body to comment out
        indent_level = len(line) - len(line.lstrip())
        for i in range(line_number, len(lines)):
            next_line = lines[i]
            if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= indent_level:
                # End of function body
                break
            # Comment out the function body
            lines[i] = f"# {next_line}"
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed redefined function in {file_path}:{line_number}")

def main():
    """Main function to fix all specified linting errors."""
    for file_path, line_number, error_code in ERRORS:
        file_path = Path(file_path)
        
        # Make sure the file exists
        if not file_path.exists():
            print(f"Warning: File {file_path} does not exist. Skipping.")
            continue
        
        # Fix the specific error
        if error_code == "F541":
            fix_f_string_missing_placeholders(file_path, line_number)
        elif error_code == "E501":
            fix_line_too_long(file_path, line_number)
        elif error_code == "F811":
            fix_redefined_function(file_path, line_number)
        else:
            print(f"Warning: Unsupported error code {error_code}. Skipping.")
    
    print("All specified errors have been addressed!")

if __name__ == "__main__":
    main()