import re
import ast


def split_args(s):
    # crude splitter for two arguments separated by ','
    parts = []
    depth = 0
    cur = ''
    for ch in s:
        if ch == ',' and depth == 0:
            parts.append(cur.strip())
            cur = ''
            continue
        cur += ch
        if ch in '([':
            depth += 1
        if ch in ')]':
            depth -= 1
    if cur.strip():
        parts.append(cur.strip())
    return parts


def eval_expr(expr, vars_):
    expr = expr.strip()
    # string literal
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        s = expr[1:-1]
        return interpolate(s, vars_)
    # concatenated strings like "Hello " {name}
    # handle simple braces and numbers
    # replace {var} occurrences
    if '{' in expr and '}' in expr:
        return interpolate(expr, vars_)
    # try number literal
    try:
        if '.' in expr:
            return float(expr)
        return int(expr)
    except Exception:
        # variable reference or list/dict access
        if '.' in expr and not expr.startswith('.'):
            # could be dict/list access
            parts = expr.split('.')
            obj = vars_.get(parts[0])
            for part in parts[1:]:
                if isinstance(obj, dict):
                    obj = obj.get(part)
                elif isinstance(obj, list):
                    try:
                        idx = int(part)
                        obj = obj[idx]
                    except:
                        obj = None
                else:
                    obj = None
            return obj
        key = expr.strip('{}')
        return vars_.get(key, None)


def interpolate(s, vars_):
    def repl(m):
        name = m.group(1)
        val = vars_.get(name)
        return str(val) if val is not None else ''
    # replace {name}
    res = re.sub(r"\{([^}]+)\}", repl, s)
    return res


def eval_condition(cond, vars_):
    # support comparisons: ==, !=, >, <, >=, <=
    ops = ['==', '!=', '>=', '<=', '>', '<']
    for op in ops:
        if op in cond:
            left, right = cond.split(op,1)
            lv = eval_expr(left.strip(), vars_)
            rv = eval_expr(right.strip(), vars_)
            try:
                if op == '==':
                    return lv == rv
                if op == '!=':
                    return lv != rv
                if op == '>=':
                    return lv >= rv
                if op == '<=':
                    return lv <= rv
                if op == '>':
                    return lv > rv
                if op == '<':
                    return lv < rv
            except Exception:
                return False
    # fallback: truthy
    v = eval_expr(cond.strip(), vars_)
    return bool(v)


def parse_args(s, vars_):
    # parse SetTitle="My Window" style args into dict
    res = {}
    if not s:
        return res
    parts = split_args(s)
    for p in parts:
        if '=' in p:
            k, v = p.split('=',1)
            res[k.strip()] = eval_expr(v.strip().strip('()'), vars_)
    return res
