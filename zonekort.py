#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-

import urllib2

import urlparse, urllib
import json

import networkx as nx

def fixurl(url):
    # turn string into unicode
    if not isinstance(url,unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass,at,hostport = parsed.netloc.partition('@')
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'),'')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'),'=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))

    # put it back together
    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))

def get_parsed_json(url):
    req = urllib2.urlopen(fixurl(url))
    encoding=req.headers['content-type'].split('charset=')[-1]
    content = unicode(req.read(), encoding)
    return json.loads(content)

operators = get_parsed_json(u"http://geo.oiorest.dk/takstzoner/operatører.json")

zone_url = u"http://geo.oiorest.dk/takstzoner.json?operatørnr={0}"

for operator in operators:
    print "Getting info for", operator['navn']
    
    zoner = get_parsed_json(zone_url.format(operator['nr']))
    
    G = nx.Graph()

    for zone in zoner:
        naboer = get_parsed_json(zone['naboer'])
        
        for nabo in naboer:
            G.add_edge(int(zone['nr']), int(nabo['nr']))
            
    f = open(u"{0}.xml".format(operator['navn']),"w+")
    nx.write_graphml(G, f)
    f.close()
    zoner = None

