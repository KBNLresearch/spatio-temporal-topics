import HTMLParser

par = HTMLParser.HTMLParser()


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

def html_unescape(string):
    return par.unescape(string)    
