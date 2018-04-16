import re, random, codecs
from datetime import datetime, timedelta, timezone
from dateutil import zoneinfo, tz


def text(text):
    return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|</span>|</a>|<span class="[a-z-]+">',
                   "",
                   str(text)
                   )
    )

def delta(nstr):
    if re.search("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", nstr):
        tstr = re.sub("\....Z", "", nstr)
        a = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
        return a.replace(tzinfo=tz.tzutc())
    elif re.search("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+00:00", nstr):
        tstr = re.sub("\+00:00", "", nstr)
        a = datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S.%f')
        return a.replace(tzinfo=tz.tzutc())
    elif re.search("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}", nstr):
        a = datetime.strptime(nstr, '%Y-%m-%d %H:%M:%S.%f')
        return a.replace(tzinfo=tz.tzutc())

def rand_w(txt_deta):
    with codecs.open(txt_deta, 'r', 'utf-8') as f:
        l = []
        for x in f:
            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
    m = len(l)
    s = random.randint(1, m)
    return l[s - 1]

