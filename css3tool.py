from parser import CSSParser
import re
from lxml.cssselect import CSSSelector
from lxml.html import fromstring
import argparse
import os.path

def get_unused_selectors(css, html):

    parser = CSSParser()
    parser.parse(css)
    root = fromstring(html)

    unused = []

    for s in parser.selectors:
        print s
        sel = CSSSelector(s)
        if len(sel(root)) == 0:
            unused.append(s)

    return unused

if __name__ == '__main__':

    desc = 'This program takes some CSS and HTML and determines which ' \
           'CSS selectors are not being used.'

    argparser = argparse.ArgumentParser(description=desc)
    argparser.add_argument(dest='css',
                           metavar='<CSS file>',
                           type=argparse.FileType('r'),
                           help='Path to a CSS file.')
    argparser.add_argument(dest='html',
                           metavar='<HTML file>',
                           type=argparse.FileType('r'),
                           help='Path to an HTML file.')

    try:
        args = argparser.parse_args()
    except IOError as e:
        argparser.error('{0}'.format(e))

    unused = get_unused_selectors(css=args.css.read(),
                                  html=args.html.read())
    print 'Unused Selectors:'
    print unused

