#!/usr/bin/env python

import xml.sax as sax
import optparse
from pprint import pprint

from pallium.ganglia import GangliaMetaDaemon
from pallium.parse import LoadingGangliaContentHandler

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option('--gmetad', help='feed data from gmetad', action='store_true')
    cli.add_option('--xml', help='feed data from XML file FILENAME', metavar='FILENAME')
    cli.add_option('-G', '--grid-regexp')
    cli.add_option('-C', '--cluster-regexp')
    cli.add_option('-H', '--host-regexp')
    return cli

def gmetad_feeder(parser):
    gmetad = GangliaMetaDaemon()
    
    for chunk in gmetad.query():
        parser.feed(chunk)

def file_feeder(parser, filename):
    for line in open(filename):
        parser.feed(line)

def parse_feed(feeder=lambda x: True, filters={}):
    parser = sax.make_parser()
    handler = LoadingGangliaContentHandler(**filters)
    parser.setContentHandler(handler)
    feeder(parser)
    return parser

if __name__ == '__main__':
    cli = create_cli()
    opts, args = cli.parse_args()

    kwargs = {}
    if opts.grid_regexp:
        kwargs['grid_expr'] = opts.grid_regexp
    if opts.cluster_regexp:
        kwargs['cluster_expr'] = opts.cluster_regexp
    if opts.host_regexp:
        kwargs['host_expr'] = opts.host_regexp

    if opts.gmetad:
        parser = parse_feed(feeder=gmetad_feeder, filters=kwargs)
    elif opts.xml:
        parser = parse_feed(feeder=lambda x: file_feeder(x, opts.xml), filters=kwargs)
    else:
        cli.error('must pick a data feed')

    pprint(parser.getContentHandler().data)

    

