import re
import ast


def split_args(s):
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
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        s = expr[1:-1]
        return interpolate(s, vars_)
    if '{' in expr and '}' in expr:
        return interpolate(expr, vars_)
    try:
        if '.' in expr:
            return float(expr)
        return int(expr)
    except Exception:
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
    res = re.sub(r"\{([^}]+)\}", repl, s)
    return res


def eval_condition(cond, vars_):
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
    v = eval_expr(cond.strip(), vars_)
    return bool(v)


def parse_args(s, vars_):
    res = {}
    if not s:
        return res
    parts = split_args(s)
    for p in parts:
        if '=' in p:
            k, v = p.split('=',1)
            res[k.strip()] = eval_expr(v.strip().strip('()'), vars_)
    return res
