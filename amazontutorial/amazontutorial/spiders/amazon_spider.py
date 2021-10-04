import scrapy
from ..items import AmazontutorialItem


class AmazonSpiderSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com']
    start_urls = [
        'https://www.amazon.com/s?k=last+30+days&i=stripbooks-intl-ship&crid=21GLXPZTSYM43&sprefix=last+30+%2Cstripbooks-intl-ship%2C407&ref=nb_sb_ss_ts-doa-p_1_8'        
        ]
    
    def parse(self, response):
        items=AmazontutorialItem()
        product_name=response.css('.a-color-base.a-text-normal::text').extract()
        product_author=response.css('.a-color-secondary .a-size-base.a-link-normal').css('::text').extract()
        product_price=response.css('.a-price-whole').css('::text').extract()
        product_imagelink=response.css('.s-image::attr(src)').extract()

        items['product_name']=product_name
        items['product_author']=product_author
        items['product_price']=product_price
        items['product_imagelink']=product_imagelink

        yield items
        next_page ='https://www.amazon.com/s?k=last+30+days&i=stripbooks-intl-ship&page=2&crid=21GLXPZTSYM43&qid=1633170272&sprefix=last+30+%2Cstripbooks-intl-ship%2C407&ref=sr_pg_'+ str(AmazonSpiderSpider.page_number)+''
        if AmazonSpiderSpider.page_number<=100:
            AmazonSpiderSpider.page_number+=1
            yield response.follow(next_page,callback=self.parse)
