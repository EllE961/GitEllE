#!/usr/bin/env python
"""
Script to fix common linting errors in the Gitelle project.
This script fixes:
1. Unused imports (F401)
2. Lines too long (E501)
3. Missing placeholders in f-strings (F541)
4. Unused local variables (F841)
5. Redefined functions (F811)
"""

import os
import re
import sys
from pathlib import Path


def remove_unused_imports(file_path):
    """Remove unused imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get all the imports
    import_pattern = re.compile(r'^\s*(?:from\s+[\w.]+\s+)?import\s+.*$', re.MULTILINE)
    imports = import_pattern.findall(content)

    # Filter out 'sys', 'os', etc. that were reported as unused
    unused_imports = [
        # Extract module name from errors like: 'sys' imported but unused
        line.split("'")[1] for line in open('paste.txt', 'r').readlines()
        if "F401" in line
    ]

    # Process each import line
    lines = content.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Check if line is an import statement
        if any(imp in line for imp in unused_imports) and not line.strip().startswith('#'):
            # For 'from module import x, y, z' type imports
            if 'from' in line and 'import' in line:
                from_part, import_part = line.split('import', 1)
                
                # Extract imported names
                imported_items = [item.strip() for item in import_part.split(',')]
                filtered_items = []
                
                # Keep only items that are not in unused_imports
                for item in imported_items:
                    # Handle 'as' aliasing
                    base_item = item.split(' as ')[0].strip()
                    if all(unused not in f"{from_part}import {base_item}" for unused in unused_imports):
                        filtered_items.append(item)
                
                # If we still have imports, reconstruct the line
                if filtered_items:
                    new_line = f"{from_part}import {', '.join(filtered_items)}"
                    filtered_lines.append(new_line)
                # Otherwise skip this line entirely
            
            # For simple 'import module' statements that are unused
            elif any(f"'{imp}'" in line for imp in unused_imports):
                # Skip this line as it's an unused import
                pass
            else:
                filtered_lines.append(line)
        else:
            filtered_lines.append(line)

    # Write back the filtered content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filtered_lines))
    
    print(f"Fixed unused imports in {file_path}")


def fix_long_lines(file_path, max_length=79):
    """Break long lines into multiple lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        if len(line.rstrip('\n')) > max_length:
            # Handle different types of lines
            
            # Function calls with multiple parameters
            if '(' in line and ')' in line and ',' in line:
                leading_whitespace = len(line) - len(line.lstrip())
                parts = re.split(r'([(),])', line.strip())
                
                # Recombine with line breaks
                new_line = parts[0]
                current_length = len(parts[0])
                
                for part in parts[1:]:
                    if current_length + len(part) > max_length - leading_whitespace:
                        new_line += '\n' + ' ' * (leading_whitespace + 4) + part
                        current_length = leading_whitespace + 4 + len(part)
                    else:
                        new_line += part
                        current_length += len(part)
                
                fixed_lines.append(' ' * leading_whitespace + new_line)
            
            # Long strings
            elif '"' in line or "'" in line:
                # Split into multiple string concatenations
                leading_whitespace = len(line) - len(line.lstrip())
                indent = ' ' * leading_whitespace
                
                # Find string boundaries
                string_match = re.search(r'(["\'])(.*?)(\1)', line)
                if string_match:
                    before_str = line[:string_match.start()]
                    string_content = string_match.group(2)
                    after_str = line[string_match.end():]
                    
                    # Split string if it's the cause of the line being too long
                    if len(before_str) + len(string_content) + 2 > max_length:
                        # Find a good breaking point
                        break_point = max_length - len(before_str) - 3  # Account for quotes and space
                        if break_point > 0:
                            first_part = string_content[:break_point]
                            second_part = string_content[break_point:]
                            
                            new_line = f"{before_str}'{first_part}' +\n{indent}    '{second_part}'{after_str}"
                            fixed_lines.append(new_line)
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            # Comments that are too long
            elif '#' in line:
                # Keep comments as-is for now
                fixed_lines.append(line)
            
            # Default case: just wrap with line continuation
            else:
                leading_whitespace = len(line) - len(line.lstrip())
                
                # Try to find good breaking points
                break_points = [' ', ',', ':', ';', '=', '+', '-', '*', '/', '(', ')', '[', ']', '{', '}']
                best_break = -1
                
                for bp in break_points:
                    pos = line.rfind(bp, 0, max_length)
                    if pos > best_break:
                        best_break = pos
                
                if best_break > 0:
                    fixed_lines.append(line[:best_break+1] + '\\\n')
                    fixed_lines.append(' ' * (leading_whitespace + 4) + line[best_break+1:])
                else:
                    # If we can't find a good break point, leave it for manual fixing
                    fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed long lines in {file_path}")


def fix_missing_placeholders(file_path):
    """Fix f-strings that are missing placeholders."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find f-strings without placeholders
    f_string_pattern = re.compile(r'f["\']([^{]*?)["\']')
    matches = f_string_pattern.findall(content)
    
    # Replace f-strings without placeholders with regular strings
    for match in matches:
        content = content.replace(f'f"{match}"', f'"{match}"')
        content = content.replace(f"f'{match}'", f"'{match}'")
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed missing placeholders in {file_path}")


def fix_unused_variables(file_path):
    """Fix unused local variables by commenting them out."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get the line numbers of unused variables
    unused_vars = {}
    with open('paste.txt', 'r') as f:
        for line in f:
            if 'F841' in line:
                parts = line.split(':')
                file_name = parts[0]
                line_num = int(parts[1])
                var_name = line.split("'")[1]
                
                if file_path.as_posix() == file_name:
                    unused_vars[line_num] = var_name
    
    # Fix the lines with unused variables
    for line_num, var_name in unused_vars.items():
        # Adjust for 0-indexed list
        idx = line_num - 1
        if 0 <= idx < len(lines):
            # Comment out the variable assignment
            if var_name in lines[idx]:
                lines[idx] = f"# Unused: {lines[idx]}"
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed unused variables in {file_path}")


def fix_redefined_functions(file_path):
    """Fix redefined functions by renaming or removing them."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get the line numbers of redefined functions
    redefined_funcs = {}
    with open('paste.txt', 'r') as f:
        for line in f:
            if 'F811' in line:
                parts = line.split(':')
                file_name = parts[0]
                line_num = int(parts[1])
                func_name = line.split("'")[1]
                original_line = int(line.split('line ')[1].split()[0])
                
                if file_path.as_posix() == file_name:
                    redefined_funcs[line_num] = (func_name, original_line)
    
    # Fix the lines with redefined functions
    for line_num, (func_name, orig_line) in redefined_funcs.items():
        # Adjust for 0-indexed list
        idx = line_num - 1
        if 0 <= idx < len(lines):
            # Comment out the redefined function
            if func_name in lines[idx]:
                lines[idx] = f"# Redefined (original at line {orig_line}): {lines[idx]}"
                
                # Look for the function body to comment out
                i = idx + 1
                indentation = len(lines[idx]) - len(lines[idx].lstrip())
                
                # Find the end of the function
                while i < len(lines):
                    # If we hit a line with less indentation, we're out of the function
                    if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indentation:
                        break
                    
                    # Comment out the function body
                    lines[i] = f"# {lines[i]}"
                    i += 1
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed redefined functions in {file_path}")


def main():
    """Main function to fix all linting errors."""
    # Get all Python files from the source directory
    src_dir = Path('src')
    tests_dir = Path('tests')
    
    all_py_files = []
    for root_dir in [src_dir, tests_dir]:
        if root_dir.exists():
            for root, _, files in os.walk(root_dir):
                for file in files:
                    if file.endswith('.py'):
                        all_py_files.append(Path(root) / file)
    
    print(f"Found {len(all_py_files)} Python files to process")
    
    # Process each file
    for file_path in all_py_files:
        print(f"Processing {file_path}...")
        
        # Fix each type of error
        remove_unused_imports(file_path)
        fix_long_lines(file_path)
        fix_missing_placeholders(file_path)
        fix_unused_variables(file_path)
        fix_redefined_functions(file_path)
    
    print("All files processed successfully!")


if __name__ == "__main__":
    main()