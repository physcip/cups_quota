#!/usr/bin/env python2

import ldap
import sys
import os

if os.path.dirname(__file__) != '':
    sys.path.append(os.path.dirname(__file__))
    os.chdir(os.path.dirname(__file__))

from config import *

def get_ldap_userlist():
    try:
        # Retrieve list of users from LDAP server
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        l = ldap.initialize(ldap_server)
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.simple_bind_s(ldap_user, ldap_password)
        results = l.search_st(ldap_base, ldap.SCOPE_SUBTREE, filterstr="(objectClass=user)", attrlist=[ldap_uid_attribute, "sn", "givenName"], timeout = 10)

        # `results` is a list containing [(cn, {'uid':[...], ...}), (...)]
        # Convert this to a dictionary containing {uid : {'sn' : ..., 'givenName' : ...}}
        uid2attribs = {}
        for r in results:
            if ldap_uid_attribute in r[1]:
                uid2attribs[r[1][ldap_uid_attribute][0]] = {attrib: r[1][attrib][0] for attrib in r[1].keys()}
	return uid2attribs

    except Exception as e:
        print("exception")
        print e
        return {}

def disablePrinting(username):
    print "Disabling printing for %s" % username
    try:
        subprocess.check_output(['dseditgroup', '-o', 'edit', '-n', ldap_node, '-u', ldap_user, '-P', ldap_password, '-a', username, '-t', 'user', noprinting_group], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_msg(e.output + "\n\n" + str(e).replace(ldap_password, 'XXXXXXXX'))

def enablePrinting(username):
    print "Enabling printing for %s" % username
    try:
        subprocess.check_output(['dseditgroup', '-o', 'edit', '-n', ldap_node, '-u', ldap_user, '-P', ldap_password, '-d', username, '-t', 'user', noprinting_group], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_msg(e.output + "\n\n" + str(e).replace(ldap_password, 'XXXXXXXX'))
