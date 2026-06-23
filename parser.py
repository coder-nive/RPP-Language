import re
from collections import deque


class ParseError(Exception):
    def __init__(self, msg, line=None):
        super().__init__(msg)
        self.line = line


class Parser:
    def __init__(self, tokens):
        self.tokens = deque(tokens)

    def parse(self):
        stmts = []
        while self.tokens:
            tok = self.tokens.popleft()
            node = self._parse_line(tok)
            if node:
                stmts.append(node)
        return stmts

    def _parse_line(self, tok):
        s = tok.raw
        line = tok.line
        if s.startswith('loop ' ) or s == 'loop inf.':
            return self._parse_block('loop', s, line)
        if s.startswith('while '):
            return self._parse_block('while', s, line)
        if s.startswith('for '):
            return self._parse_block('for', s, line)
        if s.startswith('if '):
            return self._parse_block('if', s, line)
        if s.startswith('func '):
            return self._parse_block('func', s, line)
        if s.startswith('onbutton '):
            return self._parse_block('onbutton', s, line)
        if s.startswith('onkey '):
            return self._parse_block('onkey', s, line)
        if s.startswith('onmouseclick'):
            return self._parse_block('onmouseclick', s, line)
        if s.startswith('try'):
            return self._parse_block('try', s, line)

        if s.startswith('say('):
            return {'type': 'say', 'expr': s[4:-1], 'line': line}
        if s.startswith('varnew:'):
            name = s.split(':',1)[1].strip()
            return {'type': 'varnew', 'name': name, 'line': line}
        if s.startswith('set '):
            rest = s[4:]
            if ':' not in rest:
                raise ParseError('Invalid set syntax', line)
            name, val = rest.split(':',1)
            return {'type': 'set', 'name': name.strip(), 'value': val.strip(), 'line': line}
        if s.startswith('create.window:'):
            m = re.match(r'create\.window:(\w+)(\((.*)\))?', s)
            if not m:
                raise ParseError('Invalid create.window', line)
            name = m.group(1)
            args = m.group(3) or ''
            return {'type': 'create_window', 'name': name, 'args': args, 'line': line}
        if '.gui.' in s:
            # e.g., main.gui.size("500" x "300") or main.gui.text("Hello")
            left, right = s.split('.gui.',1)
            win = left.strip()
            if right.startswith('size('):
                inner = right[5:-1]
                return {'type': 'gui_size', 'win': win, 'value': inner, 'line': line}
            if right.startswith('text('):
                return {'type': 'gui_text', 'win': win, 'value': right[5:-1], 'line': line}
            if right.startswith('image('):
                return {'type': 'gui_image', 'win': win, 'value': right[6:-1], 'line': line}
            if right.startswith('input('):
                return {'type': 'gui_input', 'win': win, 'value': right[6:-1], 'line': line}
            if right.startswith('button('):
                return {'type': 'gui_button', 'win': win, 'value': right[7:-1], 'line': line}
            if right.startswith('label('):
                return {'type': 'gui_label', 'win': win, 'value': right[6:-1], 'line': line}
            if right.startswith('label.update('):
                return {'type': 'gui_label_update', 'win': win, 'value': right[13:-1], 'line': line}
            if right.startswith('title('):
                return {'type': 'gui_title', 'win': win, 'value': right[6:-1], 'line': line}
            if right.startswith('textbox('):
                return {'type': 'gui_textbox', 'win': win, 'value': right[8:-1], 'line': line}
            if right.startswith('checkbox('):
                return {'type': 'gui_checkbox', 'win': win, 'value': right[9:-1], 'line': line}
            if right.startswith('dropdown('):
                return {'type': 'gui_dropdown', 'win': win, 'value': right[9:-1], 'line': line}
            if right.startswith('progress('):
                return {'type': 'gui_progress', 'win': win, 'value': right[9:-1], 'line': line}
        if s.startswith('main.sendnotification(') or s.endswith('.sendnotification("'):
            m = re.match(r'(\w+)\.sendnotification\((.*)\)', s)
            if m:
                return {'type': 'sendnotification', 'win': m.group(1), 'value': m.group(2), 'line': line}
        if s == 'main.close' or s.endswith('.close'):
            win = s.split('.',1)[0]
            return {'type': 'close', 'win': win, 'line': line}
        if s.startswith('onbutton '):
            return self._parse_block('onbutton', s, line)
        if s.startswith('call '):
            rest = s[5:].strip()
            if '(' in rest:
                m = re.match(r'(\w+)\((.*?)\)', rest)
                if m:
                    return {'type': 'call', 'name': m.group(1), 'args': m.group(2), 'line': line}
            return {'type': 'call', 'name': rest, 'args': '', 'line': line}
        if s.startswith('file.'):
            if s.startswith('file.write('):
                args = s[11:-1]
                return {'type': 'file_write', 'args': args, 'line': line}
            if s.startswith('file.append('):
                args = s[12:-1]
                return {'type': 'file_append', 'args': args, 'line': line}
            if s.startswith('file.read('):
                args = s[10:-1]
                return {'type': 'file_read', 'args': args, 'line': line}
            if s.startswith('file.delete('):
                args = s[12:-1]
                return {'type': 'file_delete', 'args': args, 'line': line}
        if s.startswith('listnew:'):
            name = s.split(':',1)[1].strip()
            return {'type': 'listnew', 'name': name, 'line': line}
        if '.add(' in s or '.remove(' in s:
            if '.add(' in s:
                parts = s.split('.add(')
                list_name = parts[0].strip()
                val = parts[1].rstrip(')')
                return {'type': 'list_add', 'list': list_name, 'value': val, 'line': line}
            if '.remove(' in s:
                parts = s.split('.remove(')
                list_name = parts[0].strip()
                val = parts[1].rstrip(')')
                return {'type': 'list_remove', 'list': list_name, 'value': val, 'line': line}
        if s.startswith('dictnew:'):
            name = s.split(':',1)[1].strip()
            return {'type': 'dictnew', 'name': name, 'line': line}
        if '.set(' in s:
            parts = s.split('.set(')
            dict_name = parts[0].strip()
            args = parts[1].rstrip(')')
            return {'type': 'dict_set', 'dict': dict_name, 'args': args, 'line': line}
        if s.startswith('random num:'):
            rng = s.split(':',1)[1]
            return {'type': 'random', 'range': rng, 'line': line}
        if s.startswith('wait '):
            return {'type': 'wait', 'value': s.split(' ',1)[1].strip(), 'line': line}
        if s.startswith('import '):
            arg = s.split(' ',1)[1].strip()
            return {'type': 'import', 'path': arg.strip('"') , 'line': line}
        if s.startswith('loop') and s == 'loop':
            return self._parse_block('loop', s, line)
        if s.startswith('if '):
            return self._parse_block('if', s, line)
        if s.startswith('func '):
            return self._parse_block('func', s, line)
        return {'type': 'raw', 'raw': s, 'line': line}

    def _collect_block(self, line_no):
        body = []
        while self.tokens:
            tok = self.tokens.popleft()
            if tok.raw.strip() == 'end':
                return body
            body.append(tok)
        raise ParseError('Unterminated block', line_no)

    def _parse_block(self, kind, header, line):
        if kind == 'loop':
            parts = header.split(' ',1)
            count = parts[1].strip() if len(parts) > 1 else 'inf.'
            body = self._collect_block(line)
            return {'type': 'loop', 'count': count, 'body': Parser(body).parse(), 'line': line}
        if kind == 'while':
            cond = header[6:].strip()
            body = self._collect_block(line)
            return {'type': 'while', 'cond': cond, 'body': Parser(body).parse(), 'line': line}
        if kind == 'for':
            rest = header[4:].strip()
            if ':' not in rest:
                raise ParseError('Invalid for syntax', line)
            var, rng = rest.split(':',1)
            body = self._collect_block(line)
            return {'type': 'for', 'var': var.strip(), 'range': rng.strip(), 'body': Parser(body).parse(), 'line': line}
        if kind == 'if':
            cond = header[3:].strip()
            body = self._collect_block(line)
            true_body = []
            false_body = []
            saw_else = False
            for t in body:
                if t.raw.strip() == 'else':
                    saw_else = True
                    continue
                if not saw_else:
                    true_body.append(t)
                else:
                    false_body.append(t)
            return {'type': 'if', 'cond': cond, 'true': Parser(true_body).parse(), 'false': Parser(false_body).parse(), 'line': line}
        if kind == 'func':
            rest = header[5:].strip()
            if '(' in rest:
                m = re.match(r'(\w+)\((.*?)\)', rest)
                if m:
                    name = m.group(1)
                    params = [p.strip() for p in m.group(2).split(',') if p.strip()]
                else:
                    name = rest
                    params = []
            else:
                name = rest
                params = []
            body = self._collect_block(line)
            return {'type': 'func', 'name': name, 'params': params, 'body': Parser(body).parse(), 'line': line}
        if kind == 'onbutton':
            m = re.match(r'onbutton\s+"(.+?)"', header)
            label = m.group(1) if m else header
            body = self._collect_block(line)
            return {'type': 'onbutton', 'label': label, 'body': Parser(body).parse(), 'line': line}
        if kind == 'onkey':
            m = re.match(r'onkey\s+"(.+?)"', header)
            key = m.group(1) if m else header
            body = self._collect_block(line)
            return {'type': 'onkey', 'key': key, 'body': Parser(body).parse(), 'line': line}
        if kind == 'onmouseclick':
            body = self._collect_block(line)
            return {'type': 'onmouseclick', 'body': Parser(body).parse(), 'line': line}
        if kind == 'try':
            body = self._collect_block(line)
            return {'type': 'try', 'body': Parser(body).parse(), 'line': line}
