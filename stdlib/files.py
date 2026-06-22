import os


def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(content))


def append(path, content):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(str(content))


def read(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def delete(path):
    if os.path.exists(path):
        os.remove(path)
