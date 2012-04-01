# Copyright (C) 2011 Peter Teichman

import logging
import os
import sys

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, DATETIME, ID, NUMERIC, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin

from .indexer import IrssiLogIndexer

log = logging.getLogger("urla")

class InitCommand:
    @classmethod
    def add_subparser(cls, parser):
        subparser = parser.add_parser("init", help="Initialize a new index")

        subparser.set_defaults(run=cls.run)

    @staticmethod
    def run(args):
        indexdir = "urla.index"

        schema = Schema(file=ID(stored=True), line=NUMERIC(stored=True),
                        network=ID(stored=True), channel=TEXT(stored=True),
                        when=DATETIME(stored=True), speaker=ID(), to=ID(),
                        content=TEXT(stored=True, analyzer=StemmingAnalyzer()))

        os.mkdir(indexdir)
        create_in(indexdir, schema)

class IndexCommand:
    @classmethod
    def add_subparser(cls, parser):
        subparser = parser.add_parser("index")

        subparser.set_defaults(run=cls.run)

    @staticmethod
    def run(args):
        index = open_dir("urla.index")
        indexer = IrssiLogIndexer(index)

        logdir = os.path.expanduser("~/.irssi/logs")

        for (dirpath, dirnames, filenames) in os.walk(logdir):
            if len(dirnames) != 0:
                # only index files in leaf directories
                continue

            for filename in filenames:
                indexer.index_file(os.path.join(dirpath, filename))

class ConsoleCommand:
    @classmethod
    def add_subparser(cls, parser):
        subparser = parser.add_parser("console")

        subparser.set_defaults(run=cls.run)

    @staticmethod
    def run(args):
        ix = open_dir("urla.index")

        qp = QueryParser("content", ix.schema)
        qp.add_plugin(DateParserPlugin())

        while True:
            try:
                query = unicode(raw_input("> "))
            except EOFError:
                print
                sys.exit(0)

            with ix.searcher() as searcher:
                parsed = qp.parse(query)
                print parsed

                results = searcher.search(parsed)

                for result in results:
                    timestamp = result["when"].strftime("%Y-%m-%d")

                    print "%s %s" % (timestamp,
                                     result["content"].encode("utf-8"))

class SearchCommand:
    @classmethod
    def add_subparser(cls, parser):
        subparser = parser.add_parser("search")
        subparser.add_argument("query", nargs="+")

        subparser.set_defaults(run=cls.run)

    @staticmethod
    def run(args):
        query = unicode(" ".join(args.query))

        ix = open_dir("urla.index")

        qp = QueryParser("content", ix.schema)
        qp.add_plugin(DateParserPlugin())

        with ix.searcher() as searcher:
            parsed = qp.parse(query)
            print parsed

            results = searcher.search(parsed, sortedby="when", reverse=True,
                                      limit=None)

            for result in results:
                timestamp = result["when"].strftime("%Y-%m-%d")

                print "%s %s" % (timestamp, result["content"].encode("utf-8"))
