import json

def error(e, msg="", ex=False) :
    print("ERROR {} : {}".format(msg, e))
    if ex : exit()    

def loads(data, cry=True) :
    data = None
    try :
        data = json.loads(data)
        if cry : print("LOADS SUCCESS.")
    except Exception as e :
        error(e, "LOADS")
    finally :
        return data

def dumps(data, cry=True) :
    data = None
    try :
        data = json.dumps(data)
        if cry : print("DUMPS SUCCESS.")
    except Exception as e :
        error(e, "DUMPS")
    finally :
        return data

def load(cpath, cry=True, ex=False) :
    data = None
    try :
        with open(cpath, 'r') as openfile :
            data = json.load(openfile)
            openfile.close()
        if cry : print("LOAD SUCCESS FROM [ {} ]".format(cpath))
    except UnicodeDecodeError as ude :
        with open(cpath, 'r', encoding="UTF8") as openfile :
            data = json.load(openfile)
            openfile.close()
    except Exception as e :
        error(e, "LOAD JSON FROM [ {} ]".format(cpath), ex)
    finally :
        return data


def save(cpath, data, cry=True, ex=False) :
    try :
        with open(cpath, 'w') as openfile :
            json.dump(data, openfile)
            openfile.close()
        if cry : print("SAVE SUCCESS TO [ {} ]".format(cpath))
    except Exception as e :
        error(e, "SAVE JSON TO [ {} ]".format(cpath), ex)