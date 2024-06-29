import os

def get_paths(dir=".", filter=lambda x: True):
    paths = []
    for root, _, files in os.walk(dir):
        for file in files:
            if filter(file):
                paths.append(os.path.join(root, file))
    return paths

def clear_dir(dir):
    for root, _, files in os.walk(dir):
        for file in files:
            os.remove(os.path.join(root, file))
