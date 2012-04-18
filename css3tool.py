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
    argparser.add_argument(dest='html',
                           metavar='<HTML file>',
                           type=argparse.FileType('r'),
                           help='Path to an HTML file.')
    argparser.add_argument(dest='css',
                           nargs='+',
                           metavar='<CSS files or directories>',
                           help='Paths to a CSS files or directories.')
 

    try:
        args = argparser.parse_args()
    except IOError as e:
        argparser.error('{0}'.format(e))

    # HTML string
    html_str = args.html.read()

    # Convert CSS paths provided as arguments to real path if necessary.
    css_paths = []    
    for css_path in args.css:
        css_paths.append(os.path.realpath(css_path))

    # Traverse CSS paths provided as arguments.  If the path is a
    # directory, add the files it contains recursively then remove
    # the directory from the list.
    for css_path in css_paths:
        if os.path.isdir(css_path):
            for root, dirs, files in os.walk(css_path):
                for file in files:
                    css_paths.append(os.path.join(root, file))
            css_paths.remove(css_path)

    # Remove duplicate paths.
    css_paths = list(set(css_paths))

    result = {}

    for css_path in css_paths:
        fh = open(css_path)
        css_str = fh.read()
        fh.close()
        result[css_path] = get_unused_selectors(css=css_str, html=html_str)

    print 'Unused Selectors:'
    print result

