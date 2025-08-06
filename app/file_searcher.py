
import glob
import os

from app.regex import match_pattern


def expand_file_patterns(file_args):
    """Expand glob patterns and collect all files"""
    files = []
    for arg in file_args:
        if '*' in arg or '?' in arg or '[' in arg:
            # Expand glob patterns
            expanded = glob.glob(arg)
            if expanded:
                files.extend(expanded)
            else:
                # No matches found for pattern
                files.append(arg)  # Keep original to show error
        else:
            files.append(arg)
    return files

def search_file_multiline(filename, pattern):
    """Search multiple lines in a file"""
    matches = []
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.rstrip('\n\r')  # Remove line endings
                if match_pattern(line, pattern):
                    matches.append((line_num, line))
    except FileNotFoundError:
        return None, f"grep: {filename}: No such file or directory"
    except IOError:
        return None, f"grep: {filename}: Permission denied"
    
    return matches, None

def search_recursive(directory, pattern):
    """Search recursively through directory"""
    matches = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                file_matches, error = search_file_multiline(filepath, pattern)
                if error:
                    continue  # Skip files we can't read
                if file_matches:
                    for line_num, line in file_matches:
                        matches.append((filepath, line_num, line))
            except Exception:
                continue  # Skip problematic files
    return matches