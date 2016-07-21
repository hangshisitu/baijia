# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
from os import path
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from items import Author
from items import Article
from items import Comment
import hashlib

class AuthorPipeline(object):
    dbfile="baijia.sqlite"
    def __init__(self):
        self._conn=None
        dispatcher.connect(self.initialize,signals.engine_started)
        dispatcher.connect(self.finalize,signals.engine_stopped)

    #def open_spider(self,spider):
    #    self.initialize()

   #def close_spider(self,spider):
    #    self.finalize()

    def initialize(self):
        #if  path.exists(self.dbfile):
        #    self._conn = sqlite3.connect(self.dbfile)
        #else:
        #    self._conn = self.create_table(self.dbfile)
        self._conn = sqlite3.connect(self.dbfile)
        self._conn.execute('''CREATE TABLE IF NOT EXISTS AUTHOR (id INT PRIMARY KEY NOT NULL,
                                             cid INT NOT NULL,
                                             domain TEXT NOT NULL,
                                             name TEXT,
                                             summary TEXT,
                                             actype INT,
                                             imageurl TEXT,
                                             articlenum INT,
                                             browsenum INT,
                                             updatetime REAL)''')

        self._conn.execute('''CREATE TABLE IF NOT EXISTS ARTICLE (id INT PRIMARY KEY NOT NULL,
                                             authorid INT NOT NULL,
                                             title TEXT NOT NULL,
                                             lables TEXT,
                                             quote TEXT,
                                             content TEXT,
                                             browsenum INT,
                                             upnum INT,
                                             downnum INT,
                                             images TEXT)''')
       
        self._conn.execute('''CREATE TABLE IF NOT EXISTS COMMENT (id INTEGER PRIMARY KEY,
                                             articleid INT NOT NULL,
                                             name TEXT NOT NULL,
                                             ctime INT,
                                             content TEXT,
                                             upnum INT,
                                             sfrom TEXT,
                                             ctype INT)''')
        self._conn.commit()	
                                             
    def finalize(self):
	if self._conn:
           self._conn.commit()
           self._conn.close()
           self._conn=None

    def create_table(self,dbfile):
        conn = sqlite3.connect(dbfile)
        conn.execute('''CREATE TABLE AUTHOR (id INT PRIMARY KEY NOT NULL,
                                             cid INT NOT NULL,
                                             domain TEXT NOT NULL,
                                             name TEXT,
                                             summary TEXT,
                                             actype INT,
                                             imageurl TEXT,
                                             articlenum INT,
                                             browsenum INT,
                                             updatetime REAL)''')
        conn.commit()
        return conn

    def process_item(self, item, spider):
        #self._conn.execute('REPALCE INTO AUTHOR(id,cid,domain,name,summary,actype,imageurl,articlenum,browsenum,updatetime)VALUES(?,?,?,?,?,?,?,?,?,?)',(item.id,item.cid,item.domain,item.name,item.summary,item.actype,item.imageurl,item.articlenum,item.browsenum,item.last_updated))
        if isinstance(item,Author):
            self._conn.execute('REPLACE INTO AUTHOR(id,cid,domain,name,summary,actype,imageurl,articlenum,browsenum,updatetime)VALUES(?,?,?,?,?,?,?,?,?,?)',(item['id'],item['cid'],item['domain'],item['name'],item['summary'],item['actype'],item['imageurl'],item['articlenum'],item['browsenum'],item['last_updated']))
        elif isinstance(item,Article):
            self._conn.execute('REPLACE INTO ARTICLE(id,authorid,title,lables,quote,content,images,browsenum,upnum,downnum)VALUES(?,?,?,?,?,?,?,?,?,?)',(item['id'],item['authorid'],item['title'],item['lables'],item['quote'],item['content'],item['images'],item['browsenum'],item['upnum'],item['downnum']))

        elif isinstance(item,Comment):
            self._conn.execute('REPLACE INTO COMMENT(id,name,ctime,content,articleid,upnum,sfrom,ctype)VALUES(?,?,?,?,?,?,?,?)',(item['id'],item['name'],item['ctime'],item['content'],item['articleid'],item['upnum'],item['sfrom'],item['ctype']))
	return item
 

