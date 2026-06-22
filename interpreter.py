import time
import threading
import random as pyrandom
from stdlib import utils, files as rfiles, variables as rvars
from stdlib.gui import WindowManager


class RPPError(Exception):
    def __init__(self, msg, line=None):
        super().__init__(msg)
        self.line = line


class Interpreter:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.windows = WindowManager()

    def run(self, ast):
        for node in ast:
            self._exec(node)

    def _exec(self, node):
        t = node.get('type')
        line = node.get('line')
        try:
            if t == 'say':
                text = utils.eval_expr(node['expr'], self.vars)
                print(text)
            elif t == 'varnew':
                name = node['name']
                if name in self.vars:
                    raise RPPError(f"Variable '{name}' already exists", line)
                self.vars[name] = None
            elif t == 'set':
                name = node['name']
                if name not in self.vars:
                    raise RPPError(f"Variable '{name}' does not exist", line)
                val = node['value']
                self._handle_set(name, val, line)
            elif t == 'create_window':
                self.windows.create(node['name'], utils.parse_args(node['args'], self.vars))
            elif t == 'gui_size':
                self.windows.size(node['win'], node['value'], self.vars)
            elif t == 'gui_text':
                self.windows.text(node['win'], node['value'], self.vars)
            elif t == 'gui_image':
                self.windows.image(node['win'], node['value'], self.vars)
            elif t == 'gui_input':
                res = self.windows.input(node['win'], node['value'], self.vars)
                # common convention: store in {input}
                self.vars['input'] = res
            elif t == 'gui_button':
                self.windows.button(node['win'], node['value'], self.vars)
            elif t == 'gui_label':
                self.windows.label(node['win'], node['value'], self.vars)
            elif t == 'gui_label_update':
                self.windows.label_update(node['win'], node['value'], self.vars)
            elif t == 'sendnotification':
                self.windows.sendnotification(node['win'], node['value'], self.vars)
            elif t == 'close':
                self.windows.close(node['win'])
            elif t == 'call':
                name = node['name']
                if name not in self.funcs:
                    raise RPPError(f"Function '{name}' not found", line)
                for n in self.funcs[name]:
                    self._exec(n)
            elif t == 'file_write':
                a = utils.split_args(node['args'])
                path = utils.eval_expr(a[0], self.vars)
                content = utils.eval_expr(a[1], self.vars)
                rfiles.write(path, content)
            elif t == 'file_read':
                a = utils.split_args(node['args'])
                path = utils.eval_expr(a[0], self.vars)
                self.vars['file_read'] = rfiles.read(path)
            elif t == 'file_delete':
                a = utils.split_args(node['args'])
                path = utils.eval_expr(a[0], self.vars)
                rfiles.delete(path)
            elif t == 'random':
                lo, hi = [int(x.strip()) for x in node['range'].split(',')]
                self.vars['random'] = pyrandom.randint(lo, hi)
            elif t == 'wait':
                val = float(utils.eval_expr(node['value'], self.vars))
                time.sleep(val)
            elif t == 'import':
                path = node['path']
                # simple import: tokenize, parse, run
                from lexer import Lexer
                from parser import Parser
                tokens = Lexer(path).tokenize()
                ast = Parser(tokens).parse()
                self.run(ast)
            elif t == 'loop':
                cnt = node['count']
                if cnt == 'inf.' or cnt == 'inf':
                    while True:
                        for n in node['body']:
                            self._exec(n)
                else:
                    times = int(cnt)
                    for _ in range(times):
                        for n in node['body']:
                            self._exec(n)
            elif t == 'if':
                if utils.eval_condition(node['cond'], self.vars):
                    for n in node['true']:
                        self._exec(n)
                else:
                    for n in node['false']:
                        self._exec(n)
            elif t == 'func':
                self.funcs[node['name']] = node['body']
            elif t == 'onbutton':
                label = node['label']
                # register handler
                def handler(evt=None, body=node['body']):
                    for n in body:
                        self._exec(n)
                self.windows.register_button_handler(label, handler)
            elif t == 'try':
                try:
                    for n in node['body']:
                        self._exec(n)
                except Exception as e:
                    print('R++ Runtime Exception caught:', e)
            elif t == 'raw':
                # ignore unknown raw lines
                pass
            else:
                raise RPPError(f"Unknown command: {t}", line)
        except RPPError:
            raise
        except Exception as e:
            raise RPPError(str(e), line)

    def _handle_set(self, name, val, line):
        # support arithmetic ops like +1, -1, *2, /2 or full value
        if val.startswith(('+', '-', '*', '/')):
            try:
                cur = self.vars.get(name) or 0
                num = float(val[1:])
                op = val[0]
                if op == '+':
                    res = cur + num
                elif op == '-':
                    res = cur - num
                elif op == '*':
                    res = cur * num
                else:
                    res = cur / num
                # convert to int if integer
                if res == int(res):
                    res = int(res)
                self.vars[name] = res
            except Exception as e:
                raise RPPError('Invalid math operation', line)
        else:
            # direct assignment; evaluate expressions
            self.vars[name] = utils.eval_expr(val, self.vars)
