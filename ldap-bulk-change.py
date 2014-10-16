#!/usr/bin/python3
__author__ = 'hhauer'

import os
import sys
import argparse
import configparser
import re

#http://pythonhosted.org/python3-ldap/
from ldap3 import Connection, Server, MODIFY_REPLACE

# Start by setting up argparse
parser = argparse.ArgumentParser(description='Make a bulk change to users in LDAP.')
parser.add_argument('--verbose', '-v', action='count', help="Set the verbosity level.")
parser.add_argument('--nossl', action="store_true", help="Connect without SSL.")
parser.add_argument('--environment', '-e', nargs="?", help="Use one of the environments defined in ~/.ldap_envs instead.")
# TODO: Add dry-run option to show what changes would be made.
# TODO: Make verbose do something.

# Command line environment options.
group = parser.add_argument_group('Connection Arguments', 'Details for the target LDAP server')
group.add_argument('host', nargs='?', help="The LDAP host URL.")
group.add_argument('port', nargs='?', help="The LDAP port.", default="636")
group.add_argument('bind_dn', nargs='?', help="The DN to bind as.")
group.add_argument('password', nargs='?', help="The password for the bind DN.")
group.add_argument('base_dn', nargs='?', help="The base DN from which to search.")

# The action we actually want to take.
parser.add_argument('filter', nargs=1, help="An LDAP filter to limit the DNs operated on.", default="(objectClass=*)")
parser.add_argument('change_attr', nargs=1, help="The attribute to be changed.")
parser.add_argument('regexp', nargs=1, help="A regexp used to determine the new value of change_attr.")
parser.add_argument('replace', nargs=1, help="The value to substitute into the new value of change_attr.")

args = parser.parse_args()

# Load any environment configurations.
config = configparser.ConfigParser()
config.read(['.ldap_envs', os.path.expanduser('~/.ldap_envs')])

# Build a record of the target environment.
if args.environment is not None and args.environment in config:
    target = config[args.environment]
else: #TODO: Where it make sense, make command line args overwrite .ldap_envs values.
    target = {
        'host': args.host,
        'port': args.port,
        'bind_dn': args.bind_dn,
        'password': args.password,
        'base_dn': args.base_dn,
    }

# Make sure we have all the necessary parameters one way or another.
soft_fail = False
for key in target.keys():
    if target[key] is None:
        print("No value for parameter: " + key)
        soft_fail = True

# If we hit a soft fail condition die out.
if soft_fail:
    sys.exit(1)

# Open a connection to the LDAP server.
if args.nossl:
    server = Server(target['host'], port=int(target['port']))
else:
    server = Server(target['host'], port=int(target['port']), use_ssl=True)

connection = Connection(server, user=target['bind_dn'], password=target['password'], auto_bind=True)

# Find our set of target DNs.
connection.search(target['base_dn'], args.filter[0], attributes=args.change_attr)

change_set = {}
for record in connection.response:
    change_set[record['dn']] = record['attributes'][args.change_attr[0]]

# Compile our regular expression.
regexp = re.compile(args.regexp[0])

# Calculate the new values.
for dn in change_set:
    new_values = []
    for attr in change_set[dn]:
        new_values.append(regexp.sub(args.replace[0], attr))

    change_set[dn] = {
        args.change_attr[0]: (MODIFY_REPLACE, new_values),
    }

#Set the new values in LDAP.
for dn in change_set:
    connection.modify(dn, change_set[dn])
    print("Modify: {}: {}".format(dn, connection.result['description']))

connection.unbind()