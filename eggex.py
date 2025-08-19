class SimpleRegexParser:
    def __init__(self):
        self.pattern = ""
        self.pos = 0
        
    def parse(self, pattern):
        """Parse a regex pattern into a state machine"""
        self.pattern = pattern
        self.pos = 0
        return self._parse_alternation()
    
    def _parse_alternation(self):
        """Parse alternation (| operator)"""
        branches = [self._parse_concatenation()]
        
        while self._peek() == '|':
            self._consume('|')
            branches.append(self._parse_concatenation())
            
        if len(branches) == 1:
            return branches[0]
        return {'type': 'alternation', 'branches': branches}
    
    def _parse_concatenation(self):
        """Parse concatenation of patterns"""
        elements = []
        
        while (self._peek() is not None and 
               self._peek() != ')' and 
               self._peek() != '|'):
            elements.append(self._parse_element())
            
        if len(elements) == 1:
            return elements[0]
        return {'type': 'concatenation', 'elements': elements}
    
    def _parse_element(self):
        """Parse a single element with optional quantifiers"""
        atom = self._parse_atom()
        
        # Handle quantifiers
        if self._peek() == '*':
            self._consume('*')
            return {'type': 'zero_or_more', 'child': atom}
        elif self._peek() == '+':
            self._consume('+')
            return {'type': 'one_or_more', 'child': atom}
        elif self._peek() == '?':
            self._consume('?')
            return {'type': 'zero_or_one', 'child': atom}
            
        return atom
    
    def _parse_atom(self):
        """Parse an atom (character, group, or character class)"""
        if self._peek() == '(':
            return self._parse_group()
        elif self._peek() == '[':
            return self._parse_character_class()
        elif self._peek() == '.':
            self._consume('.')
            return {'type': 'any_char'}
        else:
            return self._parse_character()
    
    def _parse_group(self):
        """Parse a group in parentheses"""
        self._consume('(')
        content = self._parse_alternation()
        self._consume(')')
        return {'type': 'group', 'content': content}
    
    def _parse_character_class(self):
        """Parse a character class like [a-z]"""
        self._consume('[')
        negated = False
        
        if self._peek() == '^':
            self._consume('^')
            negated = True
            
        ranges = []
        while self._peek() != ']' and self._peek() is not None:
            start = self._parse_character_literal()
            
            if self._peek() == '-':
                self._consume('-')
                end = self._parse_character_literal()
                ranges.append({'type': 'range', 'start': start, 'end': end})
            else:
                ranges.append({'type': 'single', 'char': start})
        
        self._consume(']')
        return {'type': 'character_class', 'negated': negated, 'ranges': ranges}
    
    def _parse_character(self):
        """Parse a single character, handling escape sequences"""
        if self._peek() == '\\':
            self._consume('\\')
            escaped_char = self._consume_any()
            
            # Handle common escape sequences
            if escaped_char == 'd':
                return {'type': 'digit'}
            elif escaped_char == 'w':
                return {'type': 'word_char'}
            elif escaped_char == 's':
                return {'type': 'whitespace'}
            elif escaped_char in r'.*+?|()[]{}^$\\':
                return {'type': 'literal', 'char': escaped_char}
            else:
                return {'type': 'literal', 'char': escaped_char}
        else:
            char = self._consume_any()
            if char in r'.*+?|()[]{}^$\\':
                raise ValueError(f"Unescaped special character: {char}")
            return {'type': 'literal', 'char': char}
    
    def _parse_character_literal(self):
        """Parse a character literal for character classes"""
        if self._peek() == '\\':
            self._consume('\\')
            return self._consume_any()
        else:
            return self._consume_any()
    
    def _peek(self):
        """Look at the next character without consuming it"""
        if self.pos < len(self.pattern):
            return self.pattern[self.pos]
        return None
    
    def _consume(self, expected):
        """Consume a specific character"""
        if self._peek() != expected:
            raise ValueError(f"Expected '{expected}', found '{self._peek()}'")
        self.pos += 1
    
    def _consume_any(self):
        """Consume any character"""
        if self.pos >= len(self.pattern):
            raise ValueError("Unexpected end of pattern")
        char = self.pattern[self.pos]
        self.pos += 1
        return char


class SimpleRegexMatcher:
    def __init__(self, pattern):
        parser = SimpleRegexParser()
        self.ast = parser.parse(pattern)
    
    def match(self, text):
        """Check if the entire text matches the pattern"""
        return self._match_node(self.ast, text, 0) == len(text)
    
    def search(self, text):
        """Search for the pattern anywhere in the text"""
        for i in range(len(text) + 1):
            if self._match_node(self.ast, text, i) is not None:
                return True
        return False
    
    def _match_node(self, node, text, position):
        """Recursively match a node against text"""
        if position > len(text):
            return None
            
        node_type = node['type']
        
        if node_type == 'literal':
            if position < len(text) and text[position] == node['char']:
                return position + 1
            return None
            
        elif node_type == 'any_char':
            if position < len(text):
                return position + 1
            return None
            
        elif node_type == 'digit':
            if position < len(text) and text[position] in '0123456789':
                return position + 1
            return None
            
        elif node_type == 'word_char':
            if (position < len(text) and 
                (text[position].isalnum() or text[position] == '_')):
                return position + 1
            return None
            
        elif node_type == 'whitespace':
            if position < len(text) and text[position] in ' \t\n\r':
                return position + 1
            return None
            
        elif node_type == 'concatenation':
            current_pos = position
            for element in node['elements']:
                result = self._match_node(element, text, current_pos)
                if result is None:
                    return None
                current_pos = result
            return current_pos
            
        elif node_type == 'alternation':
            for branch in node['branches']:
                result = self._match_node(branch, text, position)
                if result is not None:
                    return result
            return None
            
        elif node_type == 'zero_or_more':
            # Greedy matching
            current_pos = position
            while True:
                result = self._match_node(node['child'], text, current_pos)
                if result is None:
                    break
                current_pos = result
            return current_pos
            
        elif node_type == 'one_or_more':
            # Must match at least once
            result = self._match_node(node['child'], text, position)
            if result is None:
                return None
                
            # Then match zero or more times
            current_pos = result
            while True:
                next_result = self._match_node(node['child'], text, current_pos)
                if next_result is None:
                    break
                current_pos = next_result
            return current_pos
            
        elif node_type == 'zero_or_one':
            # Try to match once
            result = self._match_node(node['child'], text, position)
            if result is not None:
                return result
            # Or match zero times (succeed)
            return position
            
        elif node_type == 'group':
            return self._match_node(node['content'], text, position)
            
        elif node_type == 'character_class':
            if position >= len(text):
                return None
                
            char = text[position]
            matched = False
            
            for range_node in node['ranges']:
                if range_node['type'] == 'single':
                    if char == range_node['char']:
                        matched = True
                        break
                elif range_node['type'] == 'range':
                    if (ord(range_node['start']) <= ord(char) <= 
                        ord(range_node['end'])):
                        matched = True
                        break
            
            if (matched and not node['negated']) or (not matched and node['negated']):
                return position + 1
            return None
            
        return None


# Example usage and test function
def test_regex_parser():
    """Test the regex parser with some basic patterns"""
    
    test_cases = [
        # (pattern, test_string, expected_match)
        ("hello", "hello", True),
        ("hello", "world", False),
        ("h.llo", "hello", True),
        ("h.llo", "hxllo", True),
        ("a*b", "b", True),
        ("a*b", "ab", True),
        ("a*b", "aaab", True),
        ("a+b", "b", False),
        ("a+b", "ab", True),
        ("a+b", "aaab", True),
        ("a?b", "b", True),
        ("a?b", "ab", True),
        ("a?b", "aab", False),
        ("a|b", "a", True),
        ("a|b", "b", True),
        ("a|b", "c", False),
        ("[abc]", "a", True),
        ("[abc]", "d", False),
        ("[a-z]", "m", True),
        ("[a-z]", "A", False),
        ("[^abc]", "d", True),
        ("[^abc]", "a", False),
        (r"\d", "5", True),
        (r"\d", "a", False),
        (r"\w", "a", True),
        (r"\w", "_", True),
        (r"\w", " ", False),
    ]
    
    print("Testing Simple Regex Parser")
    print("=" * 40)
    
    for pattern, test_string, expected in test_cases:
        try:
            matcher = SimpleRegexMatcher(pattern)
            result = matcher.match(test_string)
            status = "✓" if result == expected else "✗"
            print(f"{status} Pattern: '{pattern}' -> '{test_string}': {result} (expected: {expected})")
        except Exception as e:
            print(f"✗ Pattern: '{pattern}' -> ERROR: {e}")
    
    # Test search functionality
    print("\nTesting search functionality:")
    matcher = SimpleRegexMatcher("lo")
    print(f"Search 'lo' in 'hello': {matcher.search('hello')}")  # Should be True
    print(f"Search 'lo' in 'world': {matcher.search('world')}")  # Should be False


# Run tests if this is the main module
if __name__ == "__main__":
    test_regex_parser()