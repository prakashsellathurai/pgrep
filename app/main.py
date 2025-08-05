import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!
def match_star(input_line, pattern, c):
    i = 0
    while True:
        if match_here(input_line, pattern):
            return True
        if i >= len(input_line) or (input_line[i] != c and c != '.'):
            break
        i+=1
    return False

def match_plus(input_line, pattern, c):
    i = 0
    # Require at least one match
    if i >= len(input_line) or (input_line[i] != c and c != '.'):
        return False
    while i < len(input_line) and (input_line[i] == c or c == '.'):
        i += 1
        if match_here(input_line[i:], pattern):
            return True
    return False


def match_here(input_line, pattern):
    if not pattern:
        return True
    if pattern[0] == '\0':
        return True
    if pattern[0] == '$' and len(pattern) == 1:
        return input_line == ''
 # ─── Repetition ─────────────────────────────

    if len(pattern) >= 2 and pattern[1] == '*':
        return match_star(input_line, pattern[2:], pattern[0])

    if len(pattern) >= 2 and pattern[1] == '+':
        return match_plus(input_line, pattern[2:], pattern[0])


 # ─── Escape Sequences ───────────────────────

    if pattern.startswith(r'\d'):
        if input_line and input_line[0].isdigit():
            return match_here(input_line[1:], pattern[2:])
        return False

    if pattern.startswith(r'\w'):
        if input_line and (input_line[0].isalnum() or   input_line[0] == '_'):
            return match_here(input_line[1:], pattern[2:])
        return False

   # ─── Character Classes ──────────────────────
    if pattern.startswith('['):
        closing = pattern.find(']')
        if closing == -1:
            raise RuntimeError("Unclosed [ in pattern")
        char_class = pattern[1:closing]
        negate = False 
        if char_class.startswith('^'):
            negate = True
            char_class = char_class[1:]
        if input_line:
            match = input_line[0] in char_class
            if negate:
                match = not match
            if match:
                return match_here(input_line[1:], pattern[closing+1:])
        return False

   # ─── Wildcard and Literal ───────────────────

    if input_line and (pattern[0]=='.' or pattern[0] == input_line[0]):
        return match_here(input_line[1:], pattern[1:])

    return False

def match_pattern(input_line, pattern):
    if pattern.startswith('^'):
        return match_here(input_line, pattern[1:])
    for i in range(len(input_line) + 1):
        if match_here(input_line[i:], pattern):
            return True 
    return False



def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Uncomment this block to pass the first stage
    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()

