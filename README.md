css3tool
========

What is it?
-----------

A tool for optimizing your CSS3 code, written in Python.  For instance,
you can feed it a CSS3 file and a HTML5 file and css3tool will tell you
which selectors aren't being used.

Dependencies
------------

css3tool was built using Python 2.6.1 and:

* argparse 1.2.1
* html5lib 0.95
* lxml 2.3.4
* ply 3.4

Installation
------------

    pip install argparse
    pip install html5lib
    pip install lxml
    pip install ply
    git clone <project>

Usage
-----

Help:

    python css3tool.py -h

Examples:

    python css3tool.py example/index.html example/css/1.css
    python css3tool.py example/index.html example/import.css example/page.css
    python css3tool.py example/index.html example/css
    python css3tool.py example/index.html example/page.css example/css

Debug Mode:

    python css3tool.py example/index.html example/styles.css --debug

Contributing
------------

For the love of God, yes.
