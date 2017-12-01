import os
import re

# Because Python3 returns a map for map, and python2.7 a list.
def lmap(f, l):
    if l is not None:
        return [f(x) for x in l]
    else:
        return None

def locate(pattern = r'\d+[_]', root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in re.findall(pattern, ' '.join(files)):
            yield os.path.join(path, filename)