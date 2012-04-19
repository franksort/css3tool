from parser import CSSParser
import re
from lxml.cssselect import CSSSelector
from lxml.html import fromstring
import argparse
import os.path
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)

def get_unused_selectors(css, html):

    if logger.getEffectiveLevel() == logging.DEBUG:
        debug = True
    else:
        debug = False

    parser = CSSParser(debug)
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

    desc = "                 _                \n" \
           "                '  )           /) \n" \
           "    _  _   _     -( _/_ ______//  \n" \
           "   (__/_)_/_)_(__ ) (__(_)(_)(/_  \n\n" 

    desc += 'This program takes some CSS and HTML and determines which ' \
            'CSS selectors are not being used.'

    example = 'example usage:\n' \
              '  python css3tool.py index.html 1.css\n' \
              '  python css3tool.py index.html 1.css 2.css\n' \
              '  python css3tool.py index.html example/cssdir\n' \
              '  python css3tool.py index.html 1.css example/cssdir' \

    argparser = argparse.ArgumentParser(description=desc, epilog=example,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    argparser.add_argument(dest='html',
                           metavar='<HTML file>',
                           type=argparse.FileType('r'),
                           help='path to an HTML file')
    argparser.add_argument(dest='css',
                           nargs='+',
                           metavar='<CSS file or dir>',
                           help='paths to a CSS files or directories')
    argparser.add_argument('--debug',
                           dest='debug',
                           action='store_true',
                           help='turns on debugging')

    try:
        args = argparser.parse_args()
    except IOError as e:
        argparser.error('{0}'.format(e))

    if(args.debug):
       logger.setLevel(logging.DEBUG)


    # HTML string
    html_str = args.html.read()
    print args.css
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

    print css_paths

    result = {}

    for css_path in css_paths:
        fh = open(css_path)
        css_str = fh.read()
        fh.close()
        result[css_path] = get_unused_selectors(css=css_str, html=html_str)

    print 'Unused Selectors:'
    print result

