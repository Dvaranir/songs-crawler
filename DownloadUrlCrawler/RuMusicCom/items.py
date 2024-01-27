# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TrackItem(scrapy.Item):
    init_name = scrapy.Field()
    init_artist = scrapy.Field()
    init_duration_ms = scrapy.Field()
    init_url = scrapy.Field()
    name = scrapy.Field()
    artist = scrapy.Field()
    download_url = scrapy.Field()
    duration_ms = scrapy.Field()
    crawled = scrapy.Field()
    similarity_name = scrapy.Field()
    similarity_artist = scrapy.Field()
    similarity_duration = scrapy.Field()
    similarity_score = scrapy.Field()
    similarity_sign = scrapy.Field()
