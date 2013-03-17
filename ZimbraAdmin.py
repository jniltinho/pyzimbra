#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
http://www.zemris.fer.hr/~sgros/devel/zimbra/ZimbraAdmin-v02.py
http://files.zimbra.com/docs/soap_api/8.0.2/soapapi-zimbra-doc/api-reference/index.html
'''

###########################################################################
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
# Author: Stjepan Gros <stjepan.gros@gmail.com>                           #
#                                                                         #
# Version: 20090310-dev                                                   #
#                                                                         #
###########################################################################

import sys
import httplib
import xml.dom.minidom
from xml.dom.minidom import Node

class AuthFailedError(Exception): pass

class SOAPGenericError(Exception): pass

class ZimbraConnection:

	soapAuthRequest = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
<soap:Header>
	<context xmlns="urn:zimbra"/>
</soap:Header>
<soap:Body>
	<AuthRequest xmlns="urn:zimbraAdmin">
		<name>USERNAME</name>
		<password>PASSWORD</password>
	</AuthRequest>
</soap:Body>
</soap:Envelope>"""

	headers = { "Content-type": "application/x-www-form-urlencoded",
			"Accept": "*/*" }

	def __init__(self, host, port):
		self.host = host
		self.port = port

		self.conn = httplib.HTTPSConnection(host, port)

		self.authToken = ""
		self.sessionId = ""

	def prepareSOAPRequest(self, requestPrototype):
		return requestPrototype.replace("AUTHTOKEN", self.authToken).replace("SESSIONID", self.sessionId)

	def auth(self, username, password):

		try:
			self.conn.connect()
			self.conn.request("POST", '/service/admin/soap',
					self.soapAuthRequest.replace("USERNAME", username).replace("PASSWORD", password),
					self.headers);

			response = self.conn.getresponse()
			data = response.read()
			self.conn.close()

			doc = xml.dom.minidom.parseString(data)

			if response.status != 200:
				raise AuthFailedError
	
			for node in doc.getElementsByTagName("authToken"):
				for subnode in node.childNodes:
					if subnode.nodeType == Node.TEXT_NODE:
						self.authToken = subnode.data

			for node in doc.getElementsByTagName("sessionId"):
				for subnode in node.childNodes:
					if subnode.nodeType == Node.TEXT_NODE:
						self.sessionId = subnode.data

		except:
			raise

	def sendRequest(self, request, printResponse = False):

		try:

			if printResponse:
				print self.prepareSOAPRequest(request)
				print

			self.conn.connect()
			self.conn.request("POST", '/service/admin/soap',
					self.prepareSOAPRequest(request),
					self.headers);

			response = self.conn.getresponse()
			data = response.read()
			self.conn.close()

			if printResponse:
				print data
				print

			if response.status != 200:
				raise SOAPGenericError

			doc = xml.dom.minidom.parseString(data)

		except:
			raise

		return doc


class ZimbraDomain:

	soapGetAllDistributionLists = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetAllDistributionListsRequest xmlns="urn:zimbraAdmin">
      <domain by="id">DOMAINID</domain>
    </GetAllDistributionListsRequest>
  </soap:Body>
</soap:Envelope>"""

	def __init__(self, name, zimbraID):
		self.name = name
		self.zimbraID = zimbraID

		self.attributes = {}

		self.lists = {}

		self.zimbraConnection = None

#	def __str__(self):
#
#		str = ""
#		for attr in self.attributes:
#			if isinstance(attr, 
#			str += attr + "=" + self.attributes[attr] + "\n"
#
#		return str

	def __getitem__(self, key):
		return self.attributes[key]

	def setZimbraConnection(self, zimbraConnection):
		self.zimbraConnection = zimbraConnection

	def setName(self, name):
		self.name = name

	def getName(self):
		return self.name

	def setZimbraID(self, zimbraID):
		self.zimbraID = zimbraID

	def getZimbraID(self):
		return self.zimbraID

	def setAttribute(self, attribute, value):
		self.attributes[attribute] = value

	def getAttribute(self, attribute):
		return self.attributes[attribute]

	def getAllDistributionLists(self):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapGetAllDistributionLists.replace("DOMAINID", self.zimbraID))

			for node in doc.getElementsByTagName("dl"):
				list = ZimbraDistributionList(node.attributes["name"].value)
				list.setZimbraID(node.attributes["id"].value)
				list.setZimbraConnection(self.zimbraConnection)

				self.lists[node.attributes["name"].value] = list
		except:
			raise

		return self.lists

class ZimbraAccount:

	soapAddAccountAlias = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <AddAccountAliasRequest xmlns="urn:zimbraAdmin">
      <id>ACCOUNTID</id>
      <alias>NEWALIAS</alias>
    </AddAccountAliasRequest>
  </soap:Body>
</soap:Envelope>"""

	soapRenameAccount = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <RenameAccountRequest xmlns="urn:zimbraAdmin">
      <id>ACCOUNTID</id>
      <newName>NEWNAME</newName>
    </RenameAccountRequest>
  </soap:Body>
</soap:Envelope>"""

	soapRemoveAlias = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <RemoveAccountAliasRequest xmlns="urn:zimbraAdmin">
      <id>ACCOUNTID</id>
      <alias>ALIAS</alias>
    </RemoveAccountAliasRequest>
  </soap:Body>
</soap:Envelope>"""

	soapModifyAccount = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <ModifyAccountRequest xmlns="urn:zimbraAdmin">
      <id>ACCOUNTID</id>
      MODIFIEDATTRS
    </ModifyAccountRequest>
  </soap:Body>
</soap:Envelope>"""

	soapModifyAccountAttribute = """<a n="ATTRNAME">ATTRVALUE</a>"""

	# List of multivalued attributes in Zimbra. These are handled
	# differently that the single valued ones.
	MULTI_VALUED_ATTRS = [ "objectClass", "mail", "zimbraMailAlias",
			"zimbraZimletAvailableZimlets", "zimbraAdminSavedSearches" ]


	def __init__(self, name):
		self.name = name
		self.zimbraID = ""
		self.attributes = {}
		self.zimbraConnection = None
		self.modifiedAttributes = []

	def setZimbraConnection(self, zimbraConnection):
		self.zimbraConnection = zimbraConnection

#	def __str__(self):
#
#		str = ""
#		for attr in self.attributes:
#			str += attr + "=" + self.attributes[attr] + "\n"
#
#		return str

	def __getitem__(self, key):
		return self.attributes[key]

	def setName(self, name):
		self.name = name

	def getName(self):
		return self.name

	def setZimbraID(self, zimbraID):
		self.zimbraID = zimbraID

	def getZimbraID(self):
		return self.zimbraID

	def setAttribute(self, attribute, value, manageModified = False):
		changed = False
		if attribute in self.MULTI_VALUED_ATTRS:
			try:
				if not value in self.attributes[attribute]:
					self.attributes[attribute].append(value)
					changed = True
			except:
				self.attributes[attribute] = [ value ]
				changed = True
		else:
			try:
				if manageModified and self.attributes[attribute] != value:
					changed = True
			except:
				changed = True

			self.attributes[attribute] = value

		if changed and manageModified and not attribute in self.modifiedAttributes:
			self.modifiedAttributes.append(attribute)

	def getAttribute(self, attribute):
		try:
			return self.attributes[attribute]
		except:
			return None

	def modifyAccount(self):
		if self.modifiedAttributes == []:
			return

		attributesToModify = ""
		for attr in self.modifiedAttributes:
			if self.attributes[attr] == None:
				continue

			attributesToModify += self.soapModifyAccountAttribute.replace("ATTRNAME", attr).replace("ATTRVALUE", self.attributes[attr])

		if len(attributesToModify):
			doc = self.zimbraConnection.sendRequest(
					self.soapModifyAccount.replace("ACCOUNTID", self.zimbraID).replace("MODIFIEDATTRS", attributesToModify), True)

		self.modifiedAttributes = []

	def addAlias(self, newAlias):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapAddAccountAlias.replace("ACCOUNTID", self.zimbraID).replace("NEWALIAS", newAlias))
#			try:
#				self.attributes["zimbraMailAlias"].append(newAlias)
#			except:
#				self.attributes["zimbraMailAlias"] = [ newAlias ]
		except:
			raise

	def renameAccount(self, newName):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapRenameAccount.replace("ACCOUNTID", self.zimbraID).replace("NEWNAME", newName))
		except:
			raise

	def removeAlias(self, alias):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapRemoveAlias.replace("ACCOUNTID", self.zimbraID).replace("ALIAS", alias))
		except:
			raise

	def hasAlias(self, alias):
		"""Checks if an account has a given alias and returns TRUE if so, otherwise FALSE"""

		try:
			alias1 = alias in self.attributes["mail"]
		except:
			alias1 = False

		try:
			alias2 = alias in self.attributes["zimbraMailAlias"]
		except:
			alias2 = False

		return alias1 or alias2

class ZimbraDistributionList:

	soapGetDistributionList = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetDistributionListRequest xmlns="urn:zimbraAdmin">
      <dl by="name">DISTRIBUTIONLISTNAME</dl>
    </GetDistributionListRequest>
  </soap:Body>
</soap:Envelope>"""

	soapGetDistributionListMembership = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetDistributionListMembershipRequest xmlns="urn:zimbraAdmin">
      <dl by="name">DISTRIBUTIONLISTNAME</dl>
    </GetDistributionListMembershipRequest>
  </soap:Body>
</soap:Envelope>"""

	soapAddDistributionListMember = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <AddDistributionListMemberRequest xmlns="urn:zimbraAdmin">
      <id>DISTRIBUTIONLISTID</id>
      <dlm>ACCOUNTNAME</dlm>
    </AddDistributionListMemberRequest>
  </soap:Body>
</soap:Envelope>"""

	soapDeleteDistributionListMember = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <RemoveDistributionListMemberRequest xmlns="urn:zimbraAdmin">
      <id>DISTRIBUTIONLISTID</id>
      <dlm>ACCOUNTNAME</dlm>
    </RemoveDistributionListMemberRequest>
  </soap:Body>
</soap:Envelope>"""

	zimbraConnection = None

	def __init__(self, name):
		self.name = name
		self.zimbraID = ""
		self.memberNames = []
		self.attributes = {}

	def setZimbraConnection(self, zimbraConnection):
		self.zimbraConnection = zimbraConnection

	def setName(self, name):
		self.name = name
		print self.name

	def getName(self):
		return self.name

	def setZimbraID(self, zimbraID):
		self.zimbraID = zimbraID

	def getZimbraID(self):
		return self.zimbraID

	def addMemberName(self, newMember):
		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapAddDistributionListMember.replace("DISTRIBUTIONLISTID", self.zimbraID).replace("ACCOUNTNAME", newMember))
			self.memberNames.append(newMember)

		except:
			raise

	def addMember(self, member):
		self.members[member.getName()] = member

	def removeMember(self, member):
		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapDeleteDistributionListMember.replace("DISTRIBUTIONLISTID", self.zimbraID).replace("ACCOUNTNAME", member))

		except:
			raise

	def getMemberNames(self):
		if self.memberNames == []:
			try:
				doc = self.zimbraConnection.sendRequest(
					self.soapGetDistributionList.replace("DISTRIBUTIONLISTNAME", self.name))

				for node in doc.getElementsByTagName("dlm"):
					for subnode in node.childNodes:
						if subnode.nodeType == Node.TEXT_NODE:
							self.memberNames.append(subnode.data)

			except:
				raise

		return self.memberNames

	def setAttribute(self, attribute, value):
		self.attributes[attribute] = value

	def getAttribute(self, attribute):
		return self.attributes[attribute]

	def getMembers(self):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapGetDistributionListMembership.replace("DISTRIBUTIONLISTNAME", self.name))

			for node in doc.getElementsByTagName("dlm"):
				for subnode in node.childNodes:
					if subnode.nodeType == Node.TEXT_NODE:
						self.memberNames.append(subnode.data)

		except:
			raise

		return self.memberNames

class ZimbraAdmin:

	soapGetAllDomains = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetAllDomainsRequest applyConfig="1" xmlns="urn:zimbraAdmin"/>
  </soap:Body>
</soap:Envelope>"""

	soapGetDomainByName = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetDomainRequest applyConfig="1" xmlns="urn:zimbraAdmin">
      <domain by="name">DOMAINNAME</domain>
    </GetDomainRequest>
  </soap:Body>
</soap:Envelope>"""

	soapCreateDomain = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <CreateDomainRequest xmlns="urn:zimbraAdmin">
      <name>DOMAINNAME</name>
    </CreateDomainRequest>
  </soap:Body>
</soap:Envelope>"""

	soapDeleteDomain = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <DeleteDomainRequest xmlns="urn:zimbraAdmin">
      <id>DOMAINID</id>
    </DeleteDomainRequest>
  </soap:Body>
</soap:Envelope>"""

	soapGetAllDistributionLists = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetAllDistributionListsRequest xmlns="urn:zimbraAdmin">
    </GetAllDistributionListsRequest>
  </soap:Body>
</soap:Envelope>"""

	soapGetDistributionListByName = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetDistributionListRequest xmlns="urn:zimbraAdmin">
      <dl by="name">DISTRIBUTIONLISTNAME</dl>
    </GetDistributionListRequest>
  </soap:Body>
</soap:Envelope>"""

	soapGetAllAccounts = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetAllAccountsRequest xmlns="urn:zimbraAdmin">
    </GetAllAccountsRequest>
  </soap:Body>
</soap:Envelope>"""


	soapGetAllAccountsDomain = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetAllAccountsRequest xmlns="urn:zimbraAdmin">
      <domain by="name">DOMAINNAME</domain>
    </GetAllAccountsRequest>
  </soap:Body>
</soap:Envelope>"""


	soapGetAccountByName = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <GetAccountRequest applyCos="1" xmlns="urn:zimbraAdmin">
      <account by="name">ACCOUNTNAME</account>
    </GetAccountRequest>
  </soap:Body>
</soap:Envelope>"""

	soapCreateAccount = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <CreateAccountRequest xmlns="urn:zimbraAdmin">
      <name>ACCOUNTNAME</name>
      <password>PASSWORD</password>
    </CreateAccountRequest>
  </soap:Body>
</soap:Envelope>"""

	soapDeleteAccount = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <DeleteAccountRequest xmlns="urn:zimbraAdmin">
      <id>ACCOUNTID</id>
    </DeleteAccountRequest>
  </soap:Body>
</soap:Envelope>"""

	soapCreateDistributionList = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <CreateDistributionListRequest xmlns="urn:zimbraAdmin">
      <name>DISTRIBUTIONLISTNAME</name>
    </CreateDistributionListRequest>
  </soap:Body>
</soap:Envelope>"""

	soapDeleteDistributionList = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <context xmlns="urn:zimbra">
      <authToken>AUTHTOKEN</authToken>
      <sessionId id="SESSIONID">SESSIONID</sessionId>
    </context>
  </soap:Header>
  <soap:Body>
    <DeleteDistributionListRequest xmlns="urn:zimbraAdmin">
      <id>DISTRIBUTIONLISTID</id>
    </DeleteDistributionListRequest>
  </soap:Body>
</soap:Envelope>"""

	def __init__(self, host, port):
		self.zimbraConnection = ZimbraConnection(host, port)

	def auth(self, username, password):

		try:
			self.zimbraConnection.auth(username, password)
		except:
			raise

	def getDomainByName(self, domainname):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapGetDomainByName.replace("DOMAINNAME", domainname))

			for node in doc.getElementsByTagName("domain"):
				domain = ZimbraDomain(node.attributes["name"].value,
							node.attributes["id"].value)
				domain.setZimbraConnection(self.zimbraConnection)

				for subnode in node.getElementsByTagName("a"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							domain.setAttribute(subnode.attributes["n"].value, subsubnode.data)

		except:
			raise

		return domain

	def getAllDomains(self):

		domains = []

		try:
			doc = self.zimbraConnection.sendRequest(self.soapGetAllDomains)

			for node in doc.getElementsByTagName("domain"):
				domain = ZimbraDomain(node.attributes["name"].value,
							node.attributes["id"].value)
				domain.setZimbraConnection(self.zimbraConnection)

				for subnode in node.getElementsByTagName("a"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							domain.setAttribute(subnode.attributes["n"].value, subsubnode.data)

				domains.append(domain)

		except:
			raise

		return domains

	def createDomain(self, domainname):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapCreateDomain.replace("DOMAINNAME", domainname))

			for node in doc.getElementsByTagName("domain"):
				domain = ZimbraDomain(node.attributes["name"].value,
							node.attributes["id"].value)

				for subnode in node.getElementsByTagName("a"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							domain.setAttribute(subnode.attributes["n"].value, subsubnode.data)

		except:
			raise

		return domain

	def deleteDomain(self, domain):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapDeleteDomain.replace("DOMAINID", domain.getZimbraID()))

		except:
			raise

	def getAllDistributionLists(self):

		lists = {}

		try:
			doc = self.zimbraConnection.sendRequest(self.soapGetAllDistributionLists)

			for node in doc.getElementsByTagName("dl"):
				list = ZimbraDistributionList(node.attributes["name"].value)
				list.setZimbraID(node.attributes["id"].value)
				list.setZimbraConnection(self.zimbraConnection)
	
				lists[node.attributes["name"].value] = list
		except:
			raise

		return lists

	def getDistributionListByName(self, name):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapGetDistributionListByName.replace("DISTRIBUTIONLISTNAME", name))

			list = ZimbraDistributionList(name)
			list.setZimbraConnection(self.zimbraConnection)

			for node in doc.getElementsByTagName("dl"):
				list.setZimbraID(node.attributes["id"].value)

				for subnode in node.getElementsByTagName("dlm"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							list.addMemberName(subsubnode.data)

		except:
			raise

		return list

	def _parseAccountDOM(self, doc):

		for node in doc.getElementsByTagName("account"):
			account = ZimbraAccount(node.attributes["name"].value)
			account.setZimbraID(node.attributes["id"].value)

			for subnode in node.getElementsByTagName("a"):
				for subsubnode in subnode.childNodes:
					if subsubnode.nodeType == Node.TEXT_NODE:
						account.setAttribute(subnode.attributes["n"].value, subsubnode.data)

			return account

		return None

	def getAllAccounts(self, debug = False):

		accounts = {}

		try:
			doc = self.zimbraConnection.sendRequest(self.soapGetAllAccounts, debug)

			for node in doc.getElementsByTagName("account"):
				account = ZimbraAccount(node.attributes["name"].value)
				account.setZimbraID(node.attributes["id"].value)
				account.setZimbraConnection(self.zimbraConnection)

				for subnode in node.getElementsByTagName("a"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							account.setAttribute(subnode.attributes["n"].value, subsubnode.data)

				accounts[node.attributes["name"].value] = account

		except:
			raise

		return accounts


	def getAllAccountsDomain(self, domain):

		accounts = {}

		try:
			doc = self.zimbraConnection.sendRequest(self.soapGetAllAccountsDomain.replace("DOMAINNAME", domain))

			for node in doc.getElementsByTagName("account"):
				account = ZimbraAccount(node.attributes["name"].value)
				account.setZimbraID(node.attributes["id"].value)
				account.setZimbraConnection(self.zimbraConnection)

				for subnode in node.getElementsByTagName("a"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							account.setAttribute(subnode.attributes["n"].value, subsubnode.data)

				accounts[node.attributes["name"].value] = account

		except:
			raise

		return accounts


	def getAccountByName(self, name):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapGetAccountByName.replace("ACCOUNTNAME", name))

			account = self._parseAccountDOM(doc)

		except:
			raise

		return account

	def createAccount(self, name, password):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapCreateAccount.replace("ACCOUNTNAME", name).replace("PASSWORD", password))

			for node in doc.getElementsByTagName("account"):
				account = ZimbraAccount(node.attributes["name"].value)
				account.setZimbraID(node.attributes["id"].value)

		except:
			raise

		return account

	def deleteAccount(self, account):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapDeleteAccount.replace("ACCOUNTID", account.getZimbraID()))

		except:
			raise

		return

	def createDistributionList(self, listName):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapCreateDistributionList.replace("DISTRIBUTIONLISTNAME", listName))

			list = ZimbraDistributionList(listName)
			list.setZimbraConnection(self.zimbraConnection)

			for node in doc.getElementsByTagName("dl"):
				list.setZimbraID(node.attributes["id"].value)

				for subnode in node.getElementsByTagName("dlm"):
					for subsubnode in subnode.childNodes:
						if subsubnode.nodeType == Node.TEXT_NODE:
							list.addMemberName(subsubnode.data)
		except:
			raise

		return list

	def deleteDistributionList(self, distributionList):

		try:
			doc = self.zimbraConnection.sendRequest(
					self.soapDeleteDistributionList.replace("DISTRIBUTIONLISTID", distributionList.getZimbraID()))

		except:
			raise

		return

def main():

	ZIMBRASRVIP = ""
	ZIMBRASRVADMINPORT = 7071

	ADMINUSER="admin"
	ADMINPASS="password"

	TESTDOMAIN="testdomain.hr"

	TESTACCOUNT="sgros@" + TESTDOMAIN
	TESTPASS="password1"

	TESTLIST="all@" + TESTDOMAIN

	#
	# Initiating connection to Zimbra server
	#

	conn = ZimbraAdmin(ZIMBRASRVIP, ZIMBRASRVADMINPORT)
	conn.auth(ADMINUSER, ADMINPASS)

	print "Getting list..."
	list = conn.getDistributionListByName(TESTLIST)
	print list.getMemberNames()

	sys.exit(1)

	#
	# Domain manipulation
	#
	print "Creating new domain..."
	domain = conn.createDomain(TESTDOMAIN)

	print conn.getDomainByName(TESTDOMAIN)

	print "Deleting domain..."
	conn.deleteDomain(domain)

	for i in conn.getAllDomains():
		print i

	#for user in conn.getAllAccounts():
	#	print user.getName(), user.getZimbraID()

	#
	# Account manipulation
	#
	print "Creating account..."
	account = conn.createAccount(TESTACCOUNT, TESTPASS)
	print account.getZimbraID()

	account = conn.getAccountByName(TESTACCOUNT)
	print account["zimbraPop3Enabled"]

	print "Deleting account..."
	conn.deleteAccount(account)

	#
	# Distribution list manipulation
	#
	print conn.getAllDistributionLists()

	print "Creating list..."
	dlList = conn.createDistributionList(TESTLIST)

	print "Populating list..."
	dlList = conn.getDistributionListByName(TESTLIST)

	print "Deleting list..."
	conn.deleteDistributionList(dlList)

if __name__ == "__main__":
	main()
