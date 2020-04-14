# -*- coding: utf-8 -*-
import scrapy
import re
from Fang.items import FangItem
from Fang.items import EsfItem

class FangSpider(scrapy.Spider):
    name = 'fang'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        trs = response.xpath('//div[@class="outCont"]/table/tr')
        province = None
        for tr in trs[14:20]:
            tds = tr.xpath('.//td[not(@class)]')
            province_td = tds[0]
            province_text = province_td.xpath('.//text()').get()
            province_text = re.sub(r"\s","",province_text)
            if province_text:
                province = province_text
            # 不爬取海外房源
            if province == '其它':
                continue
            city_td = tds[1]
            city_links = city_td.xpath('.//a')
            for city_link in city_links:
                city = city_link.xpath('.//text()').get()
                city_url = city_link.xpath('.//@href').get()
                # 构建新房的url链接
                url_module = city_url.split('.')
                city_newhouse_url = url_module[0]+'.newhouse.'+url_module[1]+'.'+url_module[2]+'/house/s/'
                # 构建二手房的url链接
                city_esf_url = url_module[0] + '.esf.' + url_module[1] + '.' + url_module[2]
                # print(province,city,'\t',city_url,'\t',city_newhouse_url,'\t',city_esf_url)
                yield scrapy.Request(url=city_newhouse_url, callback=self.parse_newhouse, meta={'info':(province,city)})
                yield scrapy.Request(url=city_esf_url, callback=self.parse_esf, meta={'info':(province,city)})
                break

    def parse_newhouse(self, response):
        province, city = response.meta.get('info')
        lis = response.xpath('//div[@class="nl_con clearfix"]/ul/li')
        # print("*"*30,'\n',len(lis))
        for li in lis:
            if li.xpath('./div/h3/text()').get():
                continue
            n = li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="house_value clearfix"]/div[@class="nlcd_name"]/a/text()').get()
            name = n.strip('\n').strip('\t').strip() if n else "Unknown"
            house_type = li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="house_type clearfix"]/a/text()').getall()
            rooms = '/'.join(house_type)
            a = li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="house_type clearfix"]/text()').getall()
            area = ''.join(list(map(lambda x:re.sub(r'\s','',x),a))).replace('/','').replace('－','')
            price = re.sub(r'\s','',''.join(li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="nhouse_price"]//text()').getall()))
            region = li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="relative_message clearfix"]/div[@class="address"]/a//text()').getall()
            district = re.sub(r'\s','',region[1])
            address = re.sub(r'\s','',region[2])
            status = li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="fangyuan"]/span/text()').get()
            origin_url = "https:" + li.xpath('.//div[@class="clearfix"]/div[@class="nlc_details"]/div[@class="house_value clearfix"]/div[@class="nlcd_name"]/a/@href').get()
            # print(province,city,name,rooms,area,price,district,address,status,origin_url)
            item = FangItem(province=province, city=city, name=name, rooms=rooms, area=area, price=price, district=district, address=address, status=status, origin_url=origin_url)
            yield item

        offset = response.xpath('//a[@class="next"]/@href').get()
        next_url = response.urljoin(offset)
        if offset.endswith('\4'):
            yield scrapy.Request(url=next_url, callback=self.parse_newhouse,meta={'info':(province,city)})

    def parse_esf(self, response):
        province,city = response.meta.get('info')
        dls = response.xpath('//div[@class="shop_list shop_list_4"]/dl')
        for dl in dls:
            name = dl.xpath('.//dd[1]/p[@class="add_shop"]/a/@title').get()
            try:
                p = dl.xpath('.//dd[1]/p[@class="tel_shop"]//text()').getall()
                rooms = re.sub(r'\s','',p[0])
                floor = re.sub(r'\s','',p[4])
                toward = re.sub(r'\s','',p[6])
                area = re.sub(r'\s','',p[2])
                year =re.sub(r'\s','',p[8])
            except:
                continue
            address = dl.xpath('.//dd[1]/p[@class="add_shop"]/span/text()').get()
            total_price = ''.join(dl.xpath('.//dd[@class="price_right"]/span[1]//text()').getall())
            price = dl.xpath('.//dd[@class="price_right"]/span[2]//text()').get()
            origin_url = response.url + dl.xpath('./dd[1]/h4/a/@href').get()[1:]
            print('*'*150)
            # print(province,city,name,rooms,floor,toward,area,year,address,total_price,price,origin_url)

            eitem = EsfItem(province=province,city=city,rooms=rooms,floor=floor,toward=toward,area=area,year=year,address=address,total_price=total_price,price=price,origin_url=origin_url)
            yield eitem

        # 获取下一页url进行翻页爬取
        offset = response.xpath('//div[@class="page_al"]/p[1]/a/@href').get()
        next_url = response.urljoin(offset)
        if offset.endswith('3/'):
            yield scrapy.Request(url=next_url,callback=self.parse_esf,meta={'info':(province,city)})
