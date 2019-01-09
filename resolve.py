import os
def resolve_file(name, basepath=None):
    if not basepath:
      basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath)  # os.path.join(basepath, name)
filep = resolve_file('address_parser.py')
print(filep)