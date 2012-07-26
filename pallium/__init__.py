__version__ = '0.0.1'
__author__ = 'Jon McKenzie'

import xml.sax as sax
import optparse
from pprint import pprint

from pallium.ganglia import GangliaMetaDaemon
from pallium.parse import GangliaContentHandler

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option('-G', '--grid-regexp')
    cli.add_option('-C', '--cluster-regexp')
    cli.add_option('-H', '--host-regexp')
    return cli

if __name__ == '__main__':
    cli = create_cli()
    opts, args = cli.parse_args()

    datastore = {}

    kwargs = {}
    if opts.grid_regexp:
        kwargs['grid_expr'] = opts.grid_regexp
    if opts.cluster_regexp:
        kwargs['cluster_expr'] = opts.cluster_regexp
    if opts.host_regexp:
        kwargs['host_expr'] = opts.host_regexp

    parser = sax.make_parser()
    handler = GangliaContentHandler(datastore, **kwargs)
    parser.setContentHandler(handler)

    gmetad = GangliaMetaDaemon()
    
    for chunk in gmetad.query():
        parser.feed(chunk)

    pprint(datastore)

    

