import re


class Token:
    def __init__(self, line_no, raw):
        self.line = line_no
        self.raw = raw

    def __repr__(self):
        return f"Token(line={self.line}, raw={self.raw!r})"


class Lexer:
    def __init__(self, path):
        self.path = path

    def _strip_inline_comments(self, s):
        idx = s.find('#')
        if idx != -1:
            return s[:idx]
        return s

    def tokenize(self):
        tokens = []
        in_block_comment = False
        with open(self.path, 'r', encoding='utf-8') as f:
            for i, raw in enumerate(f, start=1):
                line = raw.rstrip('\n')
                if in_block_comment:
                    if '*/' in line:
                        in_block_comment = False
                        line = line.split('*/', 1)[1]
                    else:
                        continue
                if '/*' in line:
                    parts = line.split('/*', 1)
                    line = parts[0]
                    if '*/' not in parts[1]:
                        in_block_comment = True
                line = self._strip_inline_comments(line).strip()
                if not line:
                    continue
                tokens.append(Token(i, line))
        return tokens
