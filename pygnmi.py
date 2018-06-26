#!/usr/bin/python

##############################################################################
#                                                                            #
#  pygnmi.py                                                                 #
#                                                                            #
#  History Change Log:                                                       #
#                                                                            #
#    1.0  [JGC]  2018/06/26    first version                                 #
#                                                                            #
#  Objective:                                                                #
#                                                                            #
#    Testing tool for the gNMI (GRPC Network Management Interface) in Python #
#                                                                            #
#  Features supported:                                                       #
#                                                                            #
#    - gNMI Capabilities                                                     #
#    - gNMI Subscribe (Based on Nokia SR OS release 16 feature-set)          #
#    - secure and insecure mode                                              #
#    - multiple subscriptions paths                                          #
#                                                                            #
#  Not yet supported:                                                        #
#                                                                            #
#    - Disable server name verification against TLS cert (opt: noHostCheck)  #
#    - Disable cert validation against root certificate (InsecureSkipVerify) #
#    - gNMI Get                                                              #
#    - gNMI Set                                                              #
#                                                                            #
#  License:                                                                  #
#                                                                            #
#    Licensed under the MIT license                                          #
#    See LICENSE.md delivered with this project for more information.        #
#                                                                            #
#  Author:                                                                   #
#                                                                            #
#    Sven Wisotzky [SW]                                                      #
#    mail:  sven.wisotzky(at)nokia.com                                       #
#                                                                            #
#    James Cumming [JGC]                                                     #
#    mail:  james.cumming(at)nokia.com                                       #
#                                                                            #
##############################################################################

"""
gNMI tools in Python Version 1.0
Copyright (C) 2018 Nokia. All Rights Reserved.
"""

__title__   = "pygnmi"
__version__ = "1.0"
__status__  = "dev"
__author__  = "James Cumming"
__date__    = "2018 June 26th"

##############################################################################

import argparse
import re
import sys
import os
import time
import grpc_support

##############################################################################

def get_options():
    prog = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=prog+' '+__version__)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet',   action='store_true', help='disable logging')
    group.add_argument('-v', '--verbose', action='count', help='enhanced logging')
    group = parser.add_argument_group()
    group.add_argument('--server', default='localhost:57400', help='server/port (default: localhost:57400)')
    group.add_argument('--username', default='admin', help='username (default: admin)')
    group.add_argument('--password', default='admin', help='password (default: admin)')
    group.add_argument('--cert', metavar='<filename>',  help='CA root certificate')
    group.add_argument('--tls', action='store_true', help='enable TLS security')
    group.add_argument('--ciphers', help='override environment "GRPC_SSL_CIPHER_SUITES"')
    group.add_argument('--altName', help='subjectAltName/CN override for server host validation')
    group.add_argument('--noHostCheck',  action='store_true', help='disable server host validation')

    group = parser.add_argument_group()
    group.add_argument('--logfile', metavar='<filename>', type=argparse.FileType('wb', 0), default='-', help='Specify the logfile (default: <stdout>)')
    group.add_argument('--stats', action='store_true', help='collect stats')


    group = parser.add_argument_group()
    group.add_argument('--service', default="capabilities", help='[capabilities, get, set, subscribe]')

    group = parser.add_argument_group()
    group.add_argument('--interval', default=10, type=int, help='sample interval (default: 10s)')
    group.add_argument('--timeout', type=int, help='subscription duration in seconds (default: none)')
    group.add_argument('--heartbeat', type=int, help='heartbeat interval (default: none)')
    group.add_argument('--aggregate', action='store_true', help='allow aggregation')
    group.add_argument('--suppress', action='store_true', help='suppress redundant')
    group.add_argument('--submode', default=2, type=int, help='subscription mode [TARGET_DEFINED, ON_CHANGE, SAMPLE]')
    group.add_argument('--mode', default=0, type=int, help='[STREAM, ONCE, POLL]')
    group.add_argument('--encoding', default=0, type=int, help='[JSON, BYTES, PROTO, ASCII, JSON_IETF]')
    group.add_argument('--qos', default=0, type=int, help='[JSON, BYTES, PROTO, ASCII, JSON_IETF]')
    group.add_argument('--use_alias',  action='store_true', help='use alias')
    group.add_argument('--prefix', default='', help='gRPC path prefix (default: none)')
    group.add_argument('xpaths', nargs=argparse.REMAINDER, help='path(s) to subscriber (default: /)')
    options = parser.parse_args()

    if len(options.xpaths)==0:
        options.xpaths=['/']

    if options.ciphers:
        os.environ["GRPC_SSL_CIPHER_SUITES"] = options.ciphers
    
    return(options,prog)

if __name__ == '__main__':
    (options,prog) = get_options()

    log = grpc_support.setup_log(options,prog)

    channel = grpc_support.create_channel(options,log)

    if options.service == "capabilities":
        try:
            import gNMI_Capabilities
            gNMI_Capabilities.get_capabilities(channel, options, log)
        except Exception as err:
            log.error(str(err))
            quit()

    if options.service == "subscribe":
        try:
            import gNMI_Subscribe
            gNMI_Subscribe.subscribe(channel, options,log)
        except Exception as err:
            log.error(str(err))
            quit()


