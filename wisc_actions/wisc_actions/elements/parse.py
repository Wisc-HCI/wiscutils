
def parse(classes,serialized):
    if isinstance(serialized,list):
        return [parse(classes,content) for conent in serialized]
    elif isinstance(serialized,int) or isinstance(serialized,float) or isinstance(serialized,str) or serialized == None:
        return serialized
    elif isinstance(serialized,dict):
        for cls in classes:
            for keyset in cls.keys:
                if keyset == set(serialized.keys()):
                    return cls.load(serialized)
    return serialized
    

