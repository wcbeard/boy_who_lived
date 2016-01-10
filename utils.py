from collections import namedtuple, OrderedDict
from functools import reduce
import operator as op
import re
import toolz.curried as z


Chapter = namedtuple('Chapter', 'num title text')
bookpat_re = re.compile(r'''\A(?P<title>.+)
\n*
(?:(?:.+\n+)+?)
(?P<body>
    (Chapter\ 1)
    \n+
    (.+\n*)+
)''', re.VERBOSE)

chappat_re = re.compile(r'''(Chapter (\d+)\n+((?:.+\n+)+))+''')
chapsep_re = re.compile(r'Chapter (\d+)\n(.+)\n+')


class Book(object):
    def __init__(self, title, chapters: {int: Chapter}):
        self.chapters = chapters
        self.title = title
        self.txts = OrderedDict()
        for n, chap in sorted(chapters.items()):
            setattr(self, 't{}'.format(n), chap.text)
            self.txts[n] = chap.text
        txt = reduce(op.add, self.txts.values())
        self.txt = clean_text(txt)


class BookSeries(object):
    def __init__(self, n=7):
        bks = {i: parsebook(i, vb=False) for i in range(1, n + 1)}

        self.txts = OrderedDict()
        for n, bk in sorted(bks.items()):
            setattr(self, 'b{}'.format(n), bk.txt)
            self.txts[n] = bk.txt
        txt = reduce(op.add, self.txts.values())
        self.txt = clean_text(txt)


def parsebook(fn="src/txt/hp1.txt", vb=False):
    p = print if vb else (lambda *x, **y: None)
    if isinstance(fn, int):
        fn = "src/txt/hp{}.txt".format(fn)
    p('Reading {}'.format(fn))
    with open(fn,'rb') as f:
        txt = f.read().decode("utf-8-sig")

    gd = bookpat_re.search(txt).groupdict()

    booktitle = gd['title']
    body = gd['body']

    chs = chapsep_re.split(body)[1:]
    book = {int(chnum): Chapter(int(chnum), title, text) for chnum, title, text in z.partition(3, chs)}
    return Book(booktitle, book)


def clean_text(t):
    reps = {
        '’': "'",
        '‘': "'",
        '“': '"',
        '”': '"',
        '\xad': '',
        '—': '-',
       }

    def rep(s, frto):
        fr, to = frto
        return s.replace(fr, to)
    t = reduce(rep, reps.items(), t)
    return t


def mod_axis(df, f, axis=0):
    df = df.copy()
    if not axis:
        df.index = f(df.index)
    else:
        df.columns = f(df.columns)
    return df