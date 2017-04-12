#!/usr/bin/python

import ldap.modlist
import ldap
import sys
import os

if os.path.dirname(__file__) != '':
    sys.path.append(os.path.dirname(__file__))
    os.chdir(os.path.dirname(__file__))

from config import *

ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

def get_ldap_userlist():
    try:
        # Retrieve list of users from LDAP server
        l = ldap.initialize(ldap_server)
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.simple_bind_s(ldap_user, ldap_password)
        results = l.search_st(ldap_base, ldap.SCOPE_SUBTREE, filterstr = "(objectClass=user)", attrlist = [ldap_uid_attribute, "sn", "givenName"], timeout = 10)

        # Get members of noprinting_group so that we can add the noprinting_member = True / False to users in userlist
        noprinting_results = l.search_st(ldap_base, ldap.SCOPE_SUBTREE, filterstr = "(cn=%s)" % noprinting_group, attrlist = ["member"], timeout = 10)
        if len(noprinting_results) == 0:
            error_msg(errstring + "noprinting group was not found on LDAP server.")
            return False
        noprinting_members = noprinting_results[0][1]["member"]
        print(noprinting_members)

        # `results` is a list containing [(dn, {'uid':[...], ...}), (...)]
        # Convert this to a dictionary containing {uid : {'sn' : ..., 'givenName' : ...}}
        uid2attribs = {}
        for r in results:
            if ldap_uid_attribute in r[1]:
                uid2attribs[r[1][ldap_uid_attribute][0]] = {attrib: r[1][attrib][0] for attrib in r[1].keys()}
		uid2attribs[r[1][ldap_uid_attribute][0]]["noprinting_member"] = r[0] in noprinting_members

        return uid2attribs

    except Exception as e:
        print(e)
        return {}

# Set membership (boolean) of user with username (string) in noprinting group
def set_noprinting_membership(username, membership):
    errstring = "Could not " + ("disable" if membership else "enable") + " printing for user " + username + ". "
    try:
        l = ldap.initialize(ldap_server)
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.simple_bind_s(ldap_user, ldap_password)

        # Get DN of user to add to noprinting_group
        user_results = l.search_st(ldap_base, ldap.SCOPE_SUBTREE, filterstr = "(%s=%s)" % (ldap_uid_attribute, username), timeout = 10)
        if len(user_results) == 0:
            error_msg(errstring + "User was not found on LDAP server.")
            return False
        user_dn = user_results[0][0]

        # Get DN and current members of noprinting_group
        group_results = l.search_st(ldap_base, ldap.SCOPE_SUBTREE, filterstr = "(cn=%s)" % noprinting_group, attrlist = ["member"], timeout = 10)
        if len(group_results) == 0:
            error_msg(errstring + "noprinting group was not found on LDAP server.")
            return False
        group_dn = group_results[0][0]
        group_members = group_results[0][1]["member"]

        # Add or remove member attribute to / from noprinting group
        group_members_new = list(group_members)
        if membership:
            if not user_dn in group_members_new: group_members_new.append(user_dn)
        else:
            if user_dn in group_members_new: group_members_new.remove(user_dn)

        # Abort with success in case membership is already the way it is supposed to be
        if set(group_members) == set(group_members_new):
            l.unbind_s()
            return True

        ldif = ldap.modlist.modifyModlist({"member" : group_members}, {"member" : group_members_new})
        l.modify_s(group_dn, ldif)
        l.unbind_s()
        return True
    except Exception as e:
        error_msg(errstring + "An exception occured: " + str(e))

# Returns False if action failed
def disablePrinting(username):
    print "Disabling printing for %s" % username
    return set_noprinting_membership(username, True)

# Returns False if action failed
def enablePrinting(username):
    print "Enabling printing for %s" % username
    return set_noprinting_membership(username, False)
