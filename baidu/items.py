# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class BaiduItem(scrapy.Item):
    pass

class Author(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id=scrapy.Field()
    cid=scrapy.Field()
    domain=scrapy.Field()
    name=scrapy.Field()
    summary=scrapy.Field()
    actype=scrapy.Field()
    imageurl=scrapy.Field()
    articlenum=scrapy.Field()
    browsenum=scrapy.Field()
    last_updated=scrapy.Field(serializer=str)

class Article(scrapy.Item):
    id=scrapy.Field()
    title=scrapy.Field()
    ctime=scrapy.Field()
    browsenum=scrapy.Field()
    lables=scrapy.Field()
    authorid=scrapy.Field()
    upnum=scrapy.Field()
    downnum=scrapy.Field()
    content=scrapy.Field()
    images=scrapy.Field()
    quote=scrapy.Field()

class Comment(scrapy.Item):
    id=scrapy.Field()
    articleid=scrapy.Field()
    name=scrapy.Field()
    ctime=scrapy.Field()
    content=scrapy.Field()
    upnum=scrapy.Field()
    sfrom=scrapy.Field()
    ctype=scrapy.Field()
