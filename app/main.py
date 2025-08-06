import os
import sys

from app.file_searcher import expand_file_patterns, search_file_multiline, search_recursive
from app.regex import  regex

def main():
    if len(sys.argv) < 3:
        print("Usage: python program.py -E pattern [options] [files...]", file=sys.stderr)
        exit(1)
    
    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'", file=sys.stderr)
        exit(1)
    
    pattern = sys.argv[2]
    args = sys.argv[3:]
    
    # Parse options
    recursive = False
    files = []
    
    i = 0
    while i < len(args):
        if args[i] == '-r' or args[i] == '-R':
            recursive = True
        elif args[i] == '--':
            # End of options
            files.extend(args[i+1:])
            break
        elif args[i].startswith('-'):
            # Unknown option, ignore for now
            pass
        else:
            # This is a file/directory argument
            files.extend(args[i:])
            break
        i += 1
    
    if not files:
        # stdin mode (backward compatibility)
        input_line = sys.stdin.read().strip()
        print("Logs from your program will appear here!", file=sys.stderr)
        
        if regex(input_line, pattern):
            exit(0)
        else:
            exit(1)
    
    total_matches = 0
    multiple_sources = len(files) > 1 or recursive
    
    if recursive:
        # Recursive search mode
        all_matches = []
        for file_or_dir in files:
            if os.path.isdir(file_or_dir):
                matches = search_recursive(file_or_dir, pattern)
                all_matches.extend(matches)
            else:
                # Treat as regular file even in recursive mode
                file_matches, error = search_file_multiline(file_or_dir, pattern)
                if error:
                    print(error, file=sys.stderr)
                    continue
                if file_matches:
                    for line_num, line in file_matches:
                        all_matches.append((file_or_dir, line_num, line))
        
        # Print results
        for filepath, line_num, line in all_matches:
            print(f"{filepath}:{line}")
            total_matches += 1
    
    else:
        # Regular file search (single or multiple files)
        expanded_files = expand_file_patterns(files)
        
        for filename in expanded_files:
            if os.path.isdir(filename):
                print(f"grep: {filename}: Is a directory", file=sys.stderr)
                continue
                
            file_matches, error = search_file_multiline(filename, pattern)
            
            if error:
                print(error, file=sys.stderr)
                continue
            
            if file_matches:
                for line_num, line in file_matches:
                    if multiple_sources:
                        print(f"{filename}:{line}")
                    else:
                        print(line)
                    total_matches += 1
    
    # Exit with appropriate code
    if total_matches > 0:
        exit(0)  # Success - matches found
    else:
        exit(1)  # No matches found

if __name__ == "__main__":
    main()