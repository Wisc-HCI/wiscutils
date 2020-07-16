
def parse(classes,serialized):
    for cls in classes:
        for keyset in cls.keys:
            if keyset == set(serialized.keys()):
                return cls.load(serialized)
    return serialized
