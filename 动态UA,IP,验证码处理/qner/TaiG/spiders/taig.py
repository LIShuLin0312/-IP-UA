# -*- coding: utf-8 -*-
import json
import re
import time

import requests
import scrapy
from TaiG.YDM import *

from TaiG.MySQL import Mysqlcz

from TaiG.items import TaigItem


# from lxml import etree


class TaigSpider(scrapy.Spider):
    name = 'taig'
    allowed_domains = ['travel.qunar.com']

    def start_requests(self):
        urls = Mysqlcz().getAll('select url from tg_jd_table where (city_id="1391103" and gaishu is null)')
        for url in urls:
            # print(url[0])
            ids = re.compile('-oi(\d*)-').findall(url[0])[0]
            yield scrapy.Request(url=url[0], callback=self.parse,meta={'urlx':url[0],"ids":ids})

    def parse(self, response):
        urlx = response.meta.get('urlx')
        urlr = response.url
        print(urlr)
        ids = response.meta.get('ids')
        if not response.xpath('//title/text()').extract_first() == '旅行攻略验证码':
            # ids = re.compile('/p-.{2}(\d*)-').findall(response.url)[0]

            item = TaigItem()
            imgurl = response.xpath('//ul[@id="idSlider"]/li/img/@src').extract()
            r = ''
            for i in imgurl:
                r += i
                r + '|'
            item['imgnames'] = r
            nrs = response.xpath('//div[@class="e_db_content_box"]/p//text()').extract()
            nr = ''
            for i in nrs:
                nr += i
                nr += '\n'
            item["nr"] = nr
            item["dizhi"] = response.xpath('//td[@class="td_l"]//span/text()').extract_first()
            item["kftime"] = response.xpath('//td[@class="td_r"]//span//text()').extract_first()
            item['mp'] = response.xpath('//div[@id="mp"]//p/text()').extract_first()
            item["lysj"] = response.xpath('//div[@id="lysj"]//p/text()').extract_first()
            jt = response.xpath('//div[@id="jtzn"]//p//text()').extract()
            jtzn = ''
            for i in jt:
                jtzn += i
                jtzn += '\n'
            item['jtzn'] = jtzn
            xts = ''
            xtss = response.xpath('//div[@id="ts"]//p//text()').extract()
            for i in xtss:
                xts += i
                xts += '\n'
            item['xts'] = xts
            item['urlx'] = urlx
            yield item
        # 验证码处理
        else:
            time.sleep(10)
            return
            url = response.xpath('//div//img/@src').extract_first()
            headers = {'User-Agent': "Mozilla/5.0", "Referer": urlx}
            print(headers)
            img = requests.get(url, headers=headers).content
            with open('getimage.jpg', 'wb') as f:
                f.write(img)
            y, m = yundama.decode(filename, codetype, timeout)
            print('验证码识别结果：', m)
            print('---------------------------------------------------------------------------')
            data = {
                "code": m,
                'from': "http://travel.qunar.com/place/poi/lachadahuocheyeshi-{}-".format(str(ids))
                    }
            # 提交验证码的时候一定要带入Referer,
            yield scrapy.FormRequest("http://travel.qunar.com/space/captcha/verify", formdata=data, headers=headers,
                                     callback=self.parse)
