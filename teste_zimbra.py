#!/usr/bin/env python
# -*- coding: utf-8 -*-



from ZimbraAdmin import *
import re


ZIMBRASRVIP = "zimbra.domain.com"
ZIMBRASRVADMINPORT = 7071

ADMINUSER="admin@domain.com"
ADMINPASS="pass"

conn = ZimbraAdmin(ZIMBRASRVIP, ZIMBRASRVADMINPORT)
conn.auth(ADMINUSER, ADMINPASS)


for user in conn.getAllAccountsDomain('domain.com'):
    user1 = re.sub(r'(ham.*|virus-*|spam.*|quarantine.*)', "", user)
    if user1: print user1

#account = conn.getAccountByName('teste@domain.com')
#print account["zimbraPop3Enabled"]
#print account.getZimbraID()

#print "Deleting account..."
#conn.deleteAccount(account)


#for i in conn.getAllDomains():
#	print i.name

#print "Creating account..."
#account = conn.createAccount('test@domain.com', 'pass1234')
#print account.getZimbraID()
