import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!

def find_matching_paren(pattern, start_pos):
    """Find the position of the matching closing parenthesis"""
    paren_count = 0
    for i in range(start_pos, len(pattern)):
        if pattern[i] == '(':
            paren_count += 1
        elif pattern[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                return i
    return -1

def split_alternation(pattern):
    """Split pattern by | at the top level (not inside nested groups)"""
    alternatives = []
    current = ""
    paren_depth = 0
    bracket_depth = 0
    
    i = 0
    while i < len(pattern):
        char = pattern[i]
        
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
        elif char == '|' and paren_depth == 0 and bracket_depth == 0:
            alternatives.append(current)
            current = ""
            i += 1
            continue
            
        current += char
        i += 1
    
    alternatives.append(current)
    return alternatives

def char_matches(char, pattern_char):
    """Check if character matches pattern character"""
    if pattern_char == '.':
        return True
    return char == pattern_char

def match_here(input_line, pattern, pos=0):
    """Enhanced pattern matching with support for groups and alternation"""
    if not pattern:
        return True, pos
    
    if pattern[0] == '\0':
        return True, pos
    
    if pattern[0] == '$' and len(pattern) == 1:
        return pos == len(input_line), pos
    
    # Handle groups with potential alternation and quantifiers
    if pattern.startswith('('):
        end_pos = find_matching_paren(pattern, 0)
        if end_pos == -1:
            raise RuntimeError("Unmatched parentheses")
        
        group_content = pattern[1:end_pos]
        remaining_pattern = pattern[end_pos + 1:]
        
        # Check for quantifier after group
        quantifier = None
        if remaining_pattern and remaining_pattern[0] in ['*', '+', '?']:
            quantifier = remaining_pattern[0]
            remaining_pattern = remaining_pattern[1:]
        
        # Handle group with quantifier
        if quantifier == '?':  # Optional group
            # Try matching the group
            alternatives = split_alternation(group_content)
            for alt in alternatives:
                matched, consumed = match_here(input_line, alt, pos)
                if matched:
                    # Found a match, continue with remaining pattern
                    final_matched, final_pos = match_here(input_line, remaining_pattern, consumed)
                    if final_matched:
                        return True, final_pos
            
            # No match found, try skipping the group (since it's optional)
            return match_here(input_line, remaining_pattern, pos)
            
        elif quantifier == '*':  # Zero or more
            # Try zero matches first
            matched, final_pos = match_here(input_line, remaining_pattern, pos)
            if matched:
                return True, final_pos
            
            # Try one or more matches
            current_pos = pos
            while current_pos <= len(input_line):
                alternatives = split_alternation(group_content)
                group_matched = False
                for alt in alternatives:
                    matched, consumed = match_here(input_line, alt, current_pos)
                    if matched:
                        current_pos = consumed
                        group_matched = True
                        break
                
                if not group_matched:
                    break
                    
                # Try to match remaining pattern
                matched, final_pos = match_here(input_line, remaining_pattern, current_pos)
                if matched:
                    return True, final_pos
            
            return False, pos
            
        elif quantifier == '+':  # One or more
            current_pos = pos
            match_count = 0
            
            while current_pos <= len(input_line):
                alternatives = split_alternation(group_content)
                group_matched = False
                for alt in alternatives:
                    matched, consumed = match_here(input_line, alt, current_pos)
                    if matched:
                        current_pos = consumed
                        group_matched = True
                        match_count += 1
                        break
                
                if not group_matched:
                    break
                    
                # Try to match remaining pattern
                matched, final_pos = match_here(input_line, remaining_pattern, current_pos)
                if matched and match_count > 0:
                    return True, final_pos
            
            return False, pos
            
        else:  # No quantifier
            alternatives = split_alternation(group_content)
            for alt in alternatives:
                matched, consumed = match_here(input_line, alt, pos)
                if matched:
                    return match_here(input_line, remaining_pattern, consumed)
            return False, pos
    
    # Handle character repetition
    if len(pattern) >= 2 and pattern[1] in ['*', '+', '?']:
        quantifier = pattern[1]
        char = pattern[0]
        rest_pattern = pattern[2:]
        
        if quantifier == '?':
            # Try matching one character
            if pos < len(input_line) and char_matches(input_line[pos], char):
                matched, final_pos = match_here(input_line, rest_pattern, pos + 1)
                if matched:
                    return True, final_pos
            # Try matching zero characters
            return match_here(input_line, rest_pattern, pos)
            
        elif quantifier == '*':
            # Try zero matches first
            matched, final_pos = match_here(input_line, rest_pattern, pos)
            if matched:
                return True, final_pos
            # Try one or more
            current_pos = pos
            while current_pos < len(input_line) and char_matches(input_line[current_pos], char):
                current_pos += 1
                matched, final_pos = match_here(input_line, rest_pattern, current_pos)
                if matched:
                    return True, final_pos
            return False, pos
            
        elif quantifier == '+':
            # Must match at least one
            current_pos = pos
            while current_pos < len(input_line) and char_matches(input_line[current_pos], char):
                current_pos += 1
                matched, final_pos = match_here(input_line, rest_pattern, current_pos)
                if matched:
                    return True, final_pos
            return False, pos
    
    # Handle escape sequences  
    if pattern.startswith(r'\d'):
        if pos < len(input_line) and input_line[pos].isdigit():
            return match_here(input_line, pattern[2:], pos + 1)
        return False, pos
    
    if pattern.startswith(r'\w'):
        if pos < len(input_line) and (input_line[pos].isalnum() or input_line[pos] == '_'):
            return match_here(input_line, pattern[2:], pos + 1)
        return False, pos
    
    # Handle character classes
    if pattern.startswith('['):
        closing = pattern.find(']')
        if closing == -1:
            raise RuntimeError("Unclosed [ in pattern")
        char_class = pattern[1:closing]
        negate = False
        if char_class.startswith('^'):
            negate = True
            char_class = char_class[1:]
        if pos < len(input_line):
            match = input_line[pos] in char_class
            if negate:
                match = not match
            if match:
                return match_here(input_line, pattern[closing+1:], pos + 1)
        return False, pos
    
    # Handle wildcard and literal
    if pos < len(input_line) and char_matches(input_line[pos], pattern[0]):
        return match_here(input_line, pattern[1:], pos + 1)
    
    return False, pos

# Legacy functions for backward compatibility
def match_star(input_line, pattern, c):
    matched, _ = match_here(input_line, pattern, 0)
    return matched

def match_plus(input_line, pattern, c):
    matched, _ = match_here(input_line, pattern, 0)
    return matched

def match_char(char, pattern):
    if pattern == r'\d':
        return char.isdigit()
    elif pattern == r'\w':
        return char.isalnum() or char == '_'
    else:
        return char == pattern

def match_optional(input_line, char_pattern, rest):
    matched, _ = match_here(input_line, rest, 0)
    return matched

def match_pattern(input_line, pattern):
    """Main pattern matching function"""
    if pattern.startswith('^'):
        matched, final_pos = match_here(input_line, pattern[1:])
        return matched and final_pos == len(input_line)
    
    for i in range(len(input_line) + 1):
        matched, _ = match_here(input_line[i:], pattern)
        if matched:
            return True
    return False

def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read().strip()  # Strip to remove trailing newline

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Test the pattern
    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()