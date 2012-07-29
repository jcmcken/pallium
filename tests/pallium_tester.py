#!/usr/bin/env python

import xml.sax as sax
import optparse
from pprint import pprint

from pallium.parse import AlertingGangliaContentHandler, gmetad_feeder, \
                          file_feeder, parse_feed

from pallium.alerts import load_alerts, JsonAlert
from tests import REAL_ALERTS_DIR

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option('--gmetad', help='feed data from gmetad', action='store_true')
    cli.add_option('--xml', help='feed data from XML file FILENAME', metavar='FILENAME')
    cli.add_option('--alerts-dir', help='directory containing alerts')
    return cli

if __name__ == '__main__':
    cli = create_cli()
    opts, args = cli.parse_args()

    if not opts.alerts_dir:
        opts.alerts_dir = REAL_ALERTS_DIR

    alerts = load_alerts(opts.alerts_dir, alert_cls=JsonAlert)

    handler = AlertingGangliaContentHandler(alerts)

    if opts.gmetad:
        parser = parse_feed(handler, feeder=gmetad_feeder)
    elif opts.xml:
        parser = parse_feed(handler, feeder=lambda x: file_feeder(x, opts.xml))
    else:
        cli.error('must pick a data feed')

    pprint(handler.alert_results)


    

