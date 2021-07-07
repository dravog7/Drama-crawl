#
# Types of links, 
# drama review pages - Find other reviewers
# profile review pages - find dramas and actual reviews
# Both are paginated

import scrapy


class ReviewSpider(scrapy.Spider):
    name = 'review'
    allowed_domains = ['mydramalist.com']
    start_urls = [
        'https://mydramalist.com/33898-itaewon-class/reviews',

    ]

    def parse(self, response):
        if(response.url.find('/profile/') == -1):
            #drama page
            if(response.url.find('/reviews') == -1):
                tab_link = response.css("#content .nav-tabs li")[3].css("a::attr('href')").get()
                if tab_link:
                    yield response.follow(tab_link,callback=self.parse)
            else:
                #review page
                for profile_link in response.xpath("//a[contains(@href,'/profile/')]/@href").extract():
                    yield response.follow(profile_link,callback=self.parse)
                #next page
                next_link = response.css(".page-item.next a::attr('href')").get()
                if next_link:
                    yield response.follow(next_link,callback=self.parse)
        else:
            #profile page
            if(response.url.find('/reviews') == -1):
                tab_link = response.css("#content .nav-tabs li")[2].css("a::attr('href')").get()
                if tab_link:
                    yield response.follow(tab_link,callback=self.parse)
            else:
                #review page
                for ret in self.process_reviews(response):
                    yield ret
                #next page
                next_link = response.css(".page-item.next a::attr('href')").get()
                if next_link:
                    yield response.follow(next_link,callback=self.parse)

    def process_reviews(self,response):
        #select reviews
        author = response.url.split('/')[4]
        reviews = response.xpath("//div[contains(@id,'review-')]")
        for review in reviews:
            title_link = review.css(".box-body")[0].css(".text-primary::attr('href')").get()
            title = review.css(".box-body")[0].css(".text-primary::text").get()
            ratings = review.css(".review-rating div")
            story = float(ratings[0].css("span::text").get())
            acting = float(ratings[1].css("span::text").get())
            music = float(ratings[2].css("span::text").get())
            rewatch = float(ratings[3].css("span::text").get())

            yield {
                'author': author,
                'title': title,
                'story': story,
                'acting': acting,
                'music': music,
                'rewatch': rewatch,
            }

            yield response.follow(title_link,callback=self.parse)
