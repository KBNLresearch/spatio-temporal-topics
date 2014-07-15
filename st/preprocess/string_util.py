

def string_to_unicode(string):
    try:
        return unicode(string)
    except:
        for e in ['utf-8', 'latin-1']:
            try:
                return unicode(string, e)
            except:
                pass  
    return None

    
