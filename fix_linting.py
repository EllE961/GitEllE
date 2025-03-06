#!/usr/bin/env python
"""
Script to fix syntax errors in the Gitelle project that occurred after automated fixes.
"""

import re
import sys
from pathlib import Path

# List of specific errors to fix
ERRORS = [
    ("src/gitelle/commands/branch.py", 46, "E999", "SyntaxError: invalid syntax"),
    ("src/gitelle/commands/clone.py", 48, "E999", "SyntaxError: invalid syntax. Perhaps you forgot a comma?"),
    ("src/gitelle/commands/diff.py", 159, "E131", "continuation line unaligned for hanging indent"),
    ("src/gitelle/commands/status.py", 138, "E999", "SyntaxError: unterminated string literal (detected at line 138)"),
    ("src/gitelle/core/objects.py", 171, "E999", "IndentationError: unindent does not match any outer indentation level"),
    ("src/gitelle/core/refs.py", 124, "E501", "line too long (80 > 79 characters)"),
    ("src/gitelle/core/repository.py", 204, "E999", "SyntaxError: f-string: expecting '}'")
]

def fix_syntax_error(file_path, line_number, error_code, error_message):
    """Fix syntax errors by examining the context and applying appropriate fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    if 0 <= line_number - 1 < len(lines):
        line = lines[line_number - 1]
        
        print(f"Examining line {line_number} in {file_path}:")
        print(f"Current line: {line.rstrip()}")
        
        # Different fixes based on error type
        if "invalid syntax" in error_message:
            # Check context for line breaking issues
            prev_line = lines[line_number - 2] if line_number > 1 else ""
            
            # Look for unclosed parentheses, quotes, or broken line continuation
            if prev_line.strip().endswith(('(', '[', '{')) and not line.strip().startswith((')', ']', '}')):
                # Fix indentation for continuation
                indentation = len(prev_line) - len(prev_line.lstrip())
                lines[line_number - 1] = ' ' * (indentation + 4) + line.lstrip()
                print(f"Fixed indentation for continuation line")
            
            elif prev_line.strip().endswith('\\'):
                # Fix indentation after line continuation
                indentation = len(prev_line) - len(prev_line.lstrip())
                lines[line_number - 1] = ' ' * (indentation + 4) + line.lstrip()
                print(f"Fixed indentation after line continuation")
            
            elif any(q in prev_line and q not in prev_line[prev_line.find(q)+1:] for q in ['"', "'"]):
                # Fix unclosed quotes
                # Find which quote is unclosed
                for q in ['"', "'"]:
                    if prev_line.count(q) % 2 != 0:
                        # Add closing quote at the end
                        prev_line = prev_line.rstrip() + q + '\n'
                        lines[line_number - 2] = prev_line
                        print(f"Fixed unclosed quote in previous line")
                        break
            
            else:
                # Look for potential syntax errors
                if "=" in line and "==" not in line and "!=" not in line:
                    if line.count("=") > 1 and not any(op in line for op in ["+", "-", "*", "/"]):
                        # Multiple assignments on a single line - split them
                        parts = line.split("=")
                        indentation = len(line) - len(line.lstrip())
                        indent = ' ' * indentation
                        
                        new_lines = []
                        for i in range(len(parts) - 1):
                            if i == 0:
                                new_lines.append(f"{parts[i].strip()} = {parts[i+1].strip()}")
                            else:
                                new_lines.append(f"{indent}{parts[i].strip()} = {parts[i+1].strip()}")
                        
                        for i, new_line in enumerate(new_lines):
                            if i == 0:
                                lines[line_number - 1] = new_line + '\n'
                            else:
                                lines.insert(line_number - 1 + i, new_line + '\n')
                        
                        print(f"Split multiple assignments into separate lines")
                    
                # Check for broken function call arguments
                elif "(" in line and ")" not in line:
                    next_line = lines[line_number] if line_number < len(lines) else ""
                    if not next_line.strip().startswith(')'):
                        # Add comma at the end
                        if not line.rstrip().endswith(','):
                            lines[line_number - 1] = line.rstrip() + ',\n'
                            print(f"Added missing comma")
                
                # Manual inspection message if automatic fixes don't apply
                else:
                    print(f"Syntax error requires manual inspection at line {line_number}")
                    print(f"Context: Previous line: {prev_line.rstrip()}")
                    print(f"         Current line: {line.rstrip()}")
                    print(f"ERROR: {error_message}")
        
        elif "forgot a comma" in error_message:
            # Add missing comma
            if not line.rstrip().endswith(','):
                lines[line_number - 1] = line.rstrip() + ',\n'
                print(f"Added missing comma")
        
        elif "continuation line unaligned" in error_message:
            # Fix indentation for continuation line
            prev_line = lines[line_number - 2] if line_number > 1 else ""
            indentation = len(prev_line) - len(prev_line.lstrip())
            lines[line_number - 1] = ' ' * (indentation + 4) + line.lstrip()
            print(f"Aligned continuation line")
        
        elif "unterminated string literal" in error_message:
            # Fix unclosed string
            if "'" in line and line.count("'") % 2 != 0:
                # Add closing quote
                lines[line_number - 1] = line.rstrip() + "'\n"
                print(f"Added closing quote")
            elif '"' in line and line.count('"') % 2 != 0:
                # Add closing quote
                lines[line_number - 1] = line.rstrip() + '"\n'
                print(f"Added closing quote")
            else:
                # Check for strings that might span multiple lines
                next_line = lines[line_number] if line_number < len(lines) else ""
                if not (line.rstrip().endswith('\\') and ('"' in next_line or "'" in next_line)):
                    # If it's not a properly continued string, add line continuation
                    lines[line_number - 1] = line.rstrip() + ' \\\n'
                    print(f"Added line continuation for multi-line string")
        
        elif "unindent does not match" in error_message:
            # Fix indentation
            prev_line = lines[line_number - 2] if line_number > 1 else ""
            indentation = len(prev_line) - len(prev_line.lstrip())
            
            # Look back for the outer indentation level
            outer_indent = 0
            for i in range(line_number - 2, 0, -1):
                if len(lines[i].strip()) > 0 and len(lines[i]) - len(lines[i].lstrip()) < indentation:
                    outer_indent = len(lines[i]) - len(lines[i].lstrip())
                    break
            
            # Adjust indentation
            lines[line_number - 1] = ' ' * outer_indent + line.lstrip()
            print(f"Fixed indentation to match outer level")
        
        elif "f-string: expecting '}'" in error_message:
            # Fix unclosed f-string braces
            count_open = line.count('{')
            count_close = line.count('}')
            
            if count_open > count_close:
                # Add missing closing braces
                diff = count_open - count_close
                # Find position for each unclosed brace
                positions = []
                open_positions = [i for i, char in enumerate(line) if char == '{']
                close_positions = [i for i, char in enumerate(line) if char == '}']
                
                # Match opening and closing braces
                for open_pos in open_positions:
                    matched = False
                    for close_pos in close_positions:
                        if close_pos > open_pos:
                            matched = True
                            close_positions.remove(close_pos)
                            break
                    if not matched:
                        positions.append(open_pos)
                
                # Add closing braces
                new_line = line
                for pos in sorted(positions, reverse=True):
                    # Find next non-alphanumeric character or end of string
                    end_pos = len(new_line)
                    for i in range(pos + 1, len(new_line)):
                        if not new_line[i].isalnum() and new_line[i] != '_' and new_line[i] != '.':
                            end_pos = i
                            break
                    
                    # Insert closing brace
                    new_line = new_line[:end_pos] + '}' + new_line[end_pos:]
                
                lines[line_number - 1] = new_line
                print(f"Added missing closing braces to f-string")
        
        elif "line too long" in error_code:
            # Simple line break
            if len(line) > 80:
                # Find a good breaking point
                break_point = 79
                for i in range(79, 30, -1):
                    if i < len(line) and line[i] in ' ,.:;+-*/()[]{}=':
                        break_point = i
                        break
                
                # Break the line
                indentation = len(line) - len(line.lstrip())
                first_part = line[:break_point + 1].rstrip()
                second_part = line[break_point + 1:].lstrip()
                
                if line[break_point] in ' ':
                    # Use backslash for continuation if breaking at space
                    lines[line_number - 1] = first_part + ' \\\n'
                    lines.insert(line_number, ' ' * (indentation + 4) + second_part)
                else:
                    # Otherwise just add a line break and proper indentation
                    lines[line_number - 1] = first_part + '\n'
                    lines.insert(line_number, ' ' * (indentation + 4) + second_part)
                
                print(f"Broke long line at position {break_point}")
    
    try:
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Fixed {error_code} in {file_path}:{line_number}")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

def main():
    """Main function to fix all specified syntax errors."""
    for file_path, line_number, error_code, error_message in ERRORS:
        file_path = Path(file_path)
        
        # Make sure the file exists
        if not file_path.exists():
            print(f"Warning: File {file_path} does not exist. Skipping.")
            continue
        
        # Fix the syntax error
        fix_syntax_error(file_path, line_number, error_code, error_message)
    
    print("\nAll specified syntax errors have been addressed!")
    print("Please run your linter again to check for any remaining issues.")

if __name__ == "__main__":
    main()