# wikitalk-extractor
A corpus extractor from the Wikipedia page and user talk pages

The extractor works with the "meta" Wikipedia dump, the Slovene one being http://dumps.wikimedia.org/slwiki/latest/slwiki-latest-pages-meta-current.xml.bz2.

Currently the only language specific parameter is the user tag necessary to identfy links to other users (marks the end of a comment). It can be set at the beginning of the script.

There are two modes of the extractor: extracting page talks and extracting user talks. In which mode you run the script is defined via the first argument, either being 'pagetalk' or 'usertalk'.

The XML dump is read from the standard input. The resulting XML structure is written to standard output.

Examples of running the script are:

$ bunzip2 -c slwiki-latest-pages-meta-current.xml.bz2 | ./wikitalk-extractor.py pagetalk | gzip -c > slwiki.pagetalk.gz

$ bunzip2 -c slwiki-latest-pages-meta-current.xml.bz2 | ./wikitalk-extractor.py usertalk | gzip -c > slwiki.usertalk.gz

