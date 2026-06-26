import scrapy
import json
import re
# from multiscrapper.amazon_db import amazondb
from amazon_db import amazondb
from netmeds_db import netmeds
from onemg_db import onemgdb
from pharmeasy_db import pharmeasydb
from exportsindia_db import exports_india_db



class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = [
        "amazon.in", 
        "1mg.com", 
        "netmeds.com",
        "pharmeasy.in",
        "tradeindia.com",
        "exportersindia.com"
    ]

    def start_requests(self):
        keyword_list = [
            "multivitamin",
            # "fish oil",
            # "collagen",
            # "gummies", 
            # "kids nutrition", 
            # "whey protein", 
            # "women's health"
            ]
        for keyword in keyword_list:
            # amazon_url = f"https://www.amazon.in/s?k={keyword}"
            # yield scrapy.Request(url=amazon_url, callback=self.parse_amazon)

            # netmeds_url = f"https://www.netmeds.com/ext/search/application/api/v1.0/products?filters=false&page_id=1&page_size=12&q={keyword}"
            # yield scrapy.Request(
            #     url=netmeds_url,
            #     callback=self.parse_netmeds,
            #     meta={"category": keyword}
            #     )
            
            # one_mg_url = f"https://www.1mg.com/all?name={keyword}"
            # onemg_headers = {
            #     "x-City": "New Delhi",
            #     "w-city": "New Delhi",
            #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            # }
            # one_mg_url = f"https://www.1mg.com/pwa-dweb-api/api/v4/search/all?q={keyword}&city=New%20Delhi&filter=&page_number=0&scroll_id=&per_page=10&types=sku,allopathy&sort=relevance&fetch_eta=true&is_city_serviceable=true"
            # yield scrapy.Request(
            #     url=one_mg_url,
            #     callback=self.parse_one_mg,
            #     headers=onemg_headers,
            #     meta={'category': keyword}
            #     )

            # pharmeasy_url = f"https://pharmeasy.in/search/all?name={keyword}"
            # yield scrapy.Request(
            #     url=pharmeasy_url,
            #     callback=self.parse_pharmeasy,
            #     meta={"category": keyword}
            # )

            exportsindia_url = f"https://www.exportersindia.com/search.php?srch_catg_ty=prod&term={keyword}"
            yield scrapy.Request(
                url=exportsindia_url,
                callback=self.parse_exportsindia,
                meta={"category": keyword }
            )

            # tradeindia_url = f"https://www.tradeindia.com/search.html?keyword={keyword}"
            # yield scrapy.Request(
            #     url=tradeindia_url,
            #     callback=self.parse_tradeindia,
            #     dont_filter=True,
            #     meta={"category": keyword, "ispagination": False }
            # )



    def parse_amazon(self, response):
        category = response.css("#twotabsearchtextbox").attrib['value']
        next = response.css("div[aria-label='pagination'] span.a-list-item a").attrib['href']
        next_page_url = response.urljoin(next)
        titles = response.css('div[data-cy="title-recipe"]')
        for title in titles:
            product = title.css("a h2 span::text").get()
            relative_url = title.css('a').attrib["href"]
            
            if relative_url and relative_url != 'javascript:void(0)':
                absolute_url = response.urljoin(relative_url)
                print("<-------------->")
                yield scrapy.Request(
                    url=absolute_url,
                    callback=self.parse_amazon_product_page,
                    meta={'category': category}
                    )
        
        if next_page_url and next_page_url != 'javascript.void(0)':
            yield scrapy.Request(url=next_page_url, callback=self.parse_amazon)

    def parse_amazon_product_page(self, response):
        category = response.meta['category']
        product = response.css("#productTitle::text").get()
        details = response.css("div#detailBullets_feature_div span.a-list-item")
        data = {}
        data["productname"] = product 
        for detail in details:
            title = detail.css(".a-list-item span:nth-child(1)::text").get()
            text = detail.css(".a-list-item span:nth-child(2)::text").get()
            data[title] = text
        # print(data)
        record = {
            "text": f"'{data}'",
            "category": category,
            "source": "Amazon"
            }
        print(record)
        amazondb.insert_data(record)

    def parse_netmeds(self, response):
        category = response.meta['category']
        data = json.loads(response.text)
        items = data["items"]
        page = data['page']
        for item in items:
            try:
              attributes = item['attributes']
              name = item['name']
            #   print(attributes.keys())
            #   manufactureraddress = attributes['manufactureraddress']
            #   manufacturername = attributes['manufacturername']
            #   marketername = attributes['marketername']
            #   marketeraddress = attributes['marketeraddress']
            #   record = {
            #       "name": name if name else None,
            #       "manufacturername": manufacturername if manufacturername else None,
            #       "manufactureraddress": manufactureraddress if manufactureraddress else  None,
            #       "marketername": marketername if marketername else None,
            #       "marketeraddress": marketeraddress if marketeraddress else None,
            #       "category": category if category else None
            #   }
            #   print(record)
              attributes['category'] = category
              attributes['medicine_name'] = name
              netmeds.insert_data(attributes)
            
              print("<------------>")
              print("<------------>")
            except:
                print("May be some error occurred, but who cares.")
        

        if page:
            has_next = page['has_next']
            next_id = page['next_id']
            print('has_next : ',has_next)
            print('next_id : ',next_id)
            if has_next and next_id:
                netmeds_url = f"https://www.netmeds.com/ext/search/application/api/v1.0/products?filters=false&page_id={next_id}&page_size=12&q={category}"
                yield scrapy.Request(url=netmeds_url, callback=self.parse_netmeds, meta={"category": category})

        
    def parse_one_mg(self, response):
        onemg_headers = {
                "x-City": "New Delhi",
                "w-city": "New Delhi",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        category = response.meta['category']
        api_response = json.loads(response.text)
        data = api_response.get("data", {})
        scroll_id = data.get('scroll_id')
        previous_scroll_id = data['previous_scroll_id']
        search_results = data.get('search_results', [])
        # url = /otc/zincovit-tablet-with-multivitamin-multimineral-grape-seed-extract-otc111998
        for item in search_results:
            print("<------>")
            print(scroll_id)
            item['category'] = category
            url = item.get('url')
            absolute_url = response.urljoin(url)
            # onemgdb.insert_data(item)
            if absolute_url and url:
                url_parts = url.split('/')
                name = url_parts[-1].split('-')
                name = name[0]
                yield scrapy.Request(
                    url=absolute_url,
                    callback=self.parse_onemg_product,
                    headers=onemg_headers,
                    meta={"category": category, "item": item, "name": name}
                )

            # if scroll_id:
            #     one_mg_url = f"https://www.1mg.com/pwa-dweb-api/api/v4/search/all?q={category}&city=New%20Delhi&filter=&page_number=0&scroll_id={scroll_id}&per_page=10&types=sku,allopathy&sort=relevance&fetch_eta=true&is_city_serviceable=true"
            #     yield scrapy.Request(
            #         url=one_mg_url,
            #         callback=self.parse_one_mg,
            #         headers=onemg_headers,
            #         meta={"category": category }
            #     )
        if scroll_id:
            one_mg_url = f"https://www.1mg.com/pwa-dweb-api/api/v4/search/all?q={category}&city=New%20Delhi&filter=&page_number=0&scroll_id={scroll_id}&per_page=10&types=sku,allopathy&sort=relevance&fetch_eta=true&is_city_serviceable=true"
            yield scrapy.Request(
                url=one_mg_url,
                callback=self.parse_one_mg,
                headers=onemg_headers,
                meta={"category": category}
            )
    
    def parse_onemg_product(self, response):
        category = response.meta['category']
        item = response.meta['item']
        name = response.meta['name']
        matching_scripts = [text for text in response.xpath("//script/text()").getall() if name in text.lower()]
        data = matching_scripts[len(matching_scripts) - 1]
        data = json.loads(data)
        if isinstance(data, dict):
            info = {**item, **data, "category": category}
            onemgdb.insert_data(info)
        else:
            info = {**item, "category": category}
            onemgdb.insert_data(info)

    def parse_pharmeasy(self, response):
        category = response.meta['category']
        products = response.css("div.ProductCard_medicineUnitContainer__m2_zO")
        for product in products:
            href = product.css("a").attrib['href']
            name = product.css("a h1::text").get()
            # print("name: ", name)
            # print("href: ",href)
            absolute_url = response.urljoin(href)
            yield scrapy.Request(
                url=absolute_url,
                callback=self.parse_pharmeasy_product,
                meta={"category": category, "product": name, "product_url": absolute_url}
            )
    
    def parse_pharmeasy_product(self, response):
        print("<--------------------------->")
        category = response.meta['category']
        product =  response.meta['product']
        details = response.css("div.ProductDescription_tableRow__UdxWZ")
        rows = [x for x in details]
        record = {}
        record['product_name'] = product
        record['cateory'] = category
        for row in rows:
            key = row.css("div:nth-child(1)::text").get()
            lastchild = row.css("div:last-child")
            lastchildtext = lastchild.css("div::text").get()
            spantext = lastchild.css("div span::text").get()
            if key and spantext:
                record[key] = spantext
            elif key and lastchildtext:
                record[key] = lastchildtext
        
        #add this record to db
        # pharmeasydb.insert_data(record)

        next_page = f"https://pharmeasy.in/api/search/postSearch/?highMarginOnly=false&intent_id&page=2&q={category}"
        yield scrapy.Request(
            url=next_page,
            callback=self.parse_next_pharmeasy,
            meta={"category": category }
        )
    
    def parse_next_pharmeasy(self, response):
        print("---------------------")
        category = response.meta['category']
        api_response = json.loads(response.text)
        data = api_response.get('data')
        products = data.get('products')
        for product in products:
            name = product['name']
            slug = product['slug']
            absolute_url = f"https://pharmeasy.in/health-care/products/{slug}"
            yield scrapy.Request(
                url=absolute_url,
                callback=self.parse_pharmeasy_next_product,
                meta={"category": category, "product": name }
            )
        
        hasMorePages = api_response.get('hasMorePages')
        if not hasMorePages:
            return
        
        next_page = None
        current_page = api_response['query']['page']
        print('current page: ', current_page)
        if current_page:
            next_page = int(current_page) + 1

        if next_page:
            next_page_url = f"https://pharmeasy.in/api/search/postSearch/?highMarginOnly=false&intent_id&page={next_page}&q={category}"
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_next_pharmeasy,
                meta={"category": category }
            )
        

    def parse_pharmeasy_next_product(self, response):
        category = response.meta['category']
        product =  response.meta['product']
        details = response.css("div.ProductDescription_tableRow__UdxWZ")
        rows = [x for x in details]
        record = {}
        record['product_name'] = product
        record['cateory'] = category
        for row in rows:
            key = row.css("div:nth-child(1)::text").get()
            lastchild = row.css("div:last-child")
            lastchildtext = lastchild.css("div::text").get()
            spantext = lastchild.css("div span::text").get()
            if key and spantext:
                record[key] = spantext
            elif key and lastchildtext:
                record[key] = lastchildtext
        
        # print(record)
        # pharmeasydb.insert_data(record)
    
    def parse_tradeindia(self, response):
        category = response.meta['category']
        ispagination = response.meta['ispagination']
        if ispagination:
            print("coming from pagination")

        products_details = response.css("div.product_details")
        for product in products_details:
            item = {}
            print("<------------------>")
            name = product.css("div div a h2::text").get()
            company = product.css("p.sc-3b1eb120-13::text").get()
            product_info_link = product.css("div div a").attrib['href']
            if name:
                item['name'] = name
                item['company'] = company
                item['product_info_link'] = product_info_link
                print(product_info_link)
                print(item)
                yield scrapy.Request(
                    url=product_info_link,
                    callback=self.parse_tradeindia_product,
                    dont_filter=True,
                    meta={"item": item}
                )
            else:
                break

        next_page_url = response.css("li.last-link a").attrib['href']
        if next_page_url:
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_tradeindia,
                dont_filter=True,
                meta={"category": category, "ispagination": True}
            )
    
    
    def parse_tradeindia_product(self, response):
        print("----------------------------")
        item = response.meta['item']
        table = response.css("table.spec-table tbody tr")
        record = {**item}
        for row in table:
            key = row.css("td:nth-child(1)::text").get()
            value = row.css("td:nth-child(2)::text").get()
            record[key] = value
        
        print(record)
        #add to DB
    
    def parse_exportsindia(self, response):
        category = response.meta["category"]
        products = response.css("div.inDataH")
        for product in products:
            name = product.css("h2 a::text").get()
            # print(name)
            href = product.css("h2 a").attrib['href']
            # print(href)
            yield scrapy.Request(
                url=href,
                callback=self.parse_exportsindia_product,
                meta={"category": category, "name": name }
            )
    
    def parse_exportsindia_product(self, response):
        print("<-------------------->")
        category = response.meta['category']
        product_name = response.meta['name']
        lists = response.css("div.eipdt-oi-list ul li")
        record = {"category": category, "product_name": product_name, "url": response.url}
        for list in lists:
            key = list.css("span:nth-child(1)::text").get()
            value = list.css("span:nth-child(2)::text").get()
            record[key] = value
        
        infolist = response.css("ul.pdsd-od-list li")
        for item in infolist:
            key = item.css("::text").get()
            value = item.css("span::text").get()
            record[key] = value

        print(record)
        
        # exports_india_db.insert_data(record)



