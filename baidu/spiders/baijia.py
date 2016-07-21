# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request

from baidu.items import BaiduItem
from baidu.items import Author
from baidu.items import Article
from baidu.items import Comment
import json
import time
import math
import re

class BaijiaSpider(CrawlSpider):
    name = 'baijia'
    allowed_domains = ['baijia.baidu.com']
    page=1
    pagesize=100.0
    queryauthor='http://baijia.baidu.com/ajax/getcategorywriter?ac=1&'
    ajaxcomment='http://leijun.baijia.baidu.com/ajax/commentlisttieba?url='
    categorys={"互联网":2,"文化":3,"娱乐":4,"体育":5,"财经":6,"高管":7}
    start_urls = [queryauthor+'page=%d&pagesize=%d&categoryid=%d'%(page,pagesize,cid) for cid in categorys.values()]
    pcomment=re.compile(r'ts=\d+')    
    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_start_url(self,response):
	data = json.loads(response.body_as_unicode())
        writer = data["data"]
        total = writer["total"]
        cid = self.categorys[writer["categoryName"].encode('utf-8')]
        for p in range(int(math.ceil(total/self.pagesize))):
           yield Request(self.queryauthor+'page=%d&pagesize=%d&categoryid=%d'%(p+1,self.pagesize,cid),self.parse_item)
         

    def parse_item(self, response):
	data = json.loads(response.body_as_unicode())
        writer = data["data"]
        cid = self.categorys[writer["categoryName"].encode('utf-8')]
        for w in writer["authorList"]:
	    a = Author()
            a["cid"]=cid
            a["id"]=int(w["ID"])
            a["domain"]=w["m_domain"]
	    a["name"]=w["m_name"]
            a["summary"]=w["m_summary"]
            a["actype"]=int(w["m_account_type"])
            a["imageurl"]=w["m_image_url"]
            a["articlenum"]=w["article_num"]
            a["browsenum"]=int(w["browse_num"].replace(',',''))
            a["last_updated"]=time.time()
            yield a

            yield Request('http://'+a["domain"]+'.baijia.baidu.com',self.parse_author,meta={'authorid':a['id']})
     
    def parse_author(self,response):
        #提取出文章链接,并跟随链接
        #articles = response.xpath('//div/[contains(@class,"feeds-item")]/h3/a/@href').extract()
        articles = response.css('div[class*=feeds-item] h3 a::attr(href)').extract()
        for url in articles:
            id = int(url.split('/')[-1])
            request = Request(url,meta={'id':id,'authorid':response.meta['authorid']},callback=self.parse_article)
            yield request

    def parse_article(self,response):
        article = Article()
        article['id']=response.meta['id']
        article['authorid']=response.meta['authorid']
        title=response.css('#page h1::text').extract()
        article['title']=title[0] if title else ''
        browsenum=response.css('em.readnum::text').extract()
        article['browsenum']=int(browsenum[0].replace(',','')) if browsenum else 0
        article['lables']=' '.join(response.css('a.tag::text').extract())
        quote=response.css('blockquote::text').extract()
        article['quote']= quote[0] if quote else ''
        upnum=response.css('#up_article span.num::text').extract()
        article['upnum']=int(upnum[0].replace(',','')) if upnum else 0
        downnum=response.css('#down_article span.num::text').extract()
        article['downnum']=int(downnum[0].replace(',','')) if downnum else 0
        article['content']=' '.join(response.css('.article-detail p.text::text').extract())
        article['images']=' '.join(response.css('.article-detail p.image img::attr(src)').extract())
        yield article
        yield Request(self.ajaxcomment+response.url+'&ts=0',meta={'aid':article['id']},callback=self.parse_comment)

    def parse_comment(self,response):
	rsp = json.loads(response.body_as_unicode())
        data = rsp['data']
        for comm in data['comments']:
            comment=Comment()
            comment['id']=int(comm['id'])
            comment['name']=comm['user_name']
            comment['ctime']=int(comm['ts'])
            comment['content']=comm['text']
            comment['articleid']=response.meta['aid']
            comment['upnum']=int(comm['support_count'])
            comment['sfrom']=comm['from']
            comment['ctype']=0
            if 'vip_comments' in data.keys():
                for vip in data['vip_comments']:
	            if vip['id']==comment['id']:
	                comment['cytpe'] +=1
                        break
            if 'hot_comments' in data.keys():
                for hot in data['hot_comments']:
                    if hot['id']==comment['id']:
                        comment['ctype'] +=2
                        break
            yield comment
        if data['hasmore']:
            url = self.pcomment.sub('ts='+str(comment['ctime']),response.url)
            yield Request(url,meta={'aid':response.meta['aid']},callback=self.parse_comment)
