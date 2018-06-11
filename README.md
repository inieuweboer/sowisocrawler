# sowisocrawler
Scrapy crawler for downloading files from the SOWISO learning environment


Howto:
- **Usage**:
  - Start virtualenv (optional) with virtualenv and virtualenvwrapper: `mkvirtualenv sowiso`
  - Install requirements: `pip install scrapy selenium`
  - Edit `start_urls` in `sowisocrawler/spiders/SowisoSpider.py` with links from the teacher environment in sowiso
  - Add user credentials to `sowisocrawler/login.py`
  - Start crawler with `scrapy crawl SowisoSpider`

Note that this script does not sort out students in groups (yet)
