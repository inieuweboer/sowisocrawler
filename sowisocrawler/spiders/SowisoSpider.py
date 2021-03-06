# Version 2.0, for scrapy 1.5.0

from scrapy.spiders.init import InitSpider
from scrapy.http import Request
from scrapy.shell import inspect_response

from selenium import webdriver

import logging, time, os, sys, re, unicodedata
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login import username, password  # two variables used in get_cookies()


def slugify(value):
    # Normalizes string, converts to lowercase, removes non-alpha characters,
    # and converts spaces to hyphens.
    value = unicodedata.normalize('NFKD', value) \
            .encode('ascii', 'ignore').decode('utf-8')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)

    return value


class SowisoSpider(InitSpider):
    name = "SowisoSpider"
    allowed_domains = ['uva.sowiso.nl']

    login_page = 'https://uva.sowiso.nl'
    # teacher_page = 'https://uva.sowiso.nl/profile/'
    start_urls = ['https://uva.sowiso.nl/teacher/review_test/131/1092',
                  'https://uva.sowiso.nl/teacher/review_test/131/1091']

    save_dir = '/home/inieuweboer/Desktop/InlProg2018/download'

    log_file = str(datetime.utcnow().strftime('%m_%d_%Y_%I_%M_%S')) + '.log'
    logging.basicConfig(
        filename=log_file,
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def init_request(self):
        """This function is called before crawling starts."""
        self.cookies = self.get_cookies()
        return Request(url=self.login_page,
                       cookies=self.cookies,
                       callback=self.check_login)

    def get_cookies(self):
        driver = webdriver.Firefox()
        driver.get(self.login_page)
        time.sleep(3)
        username_el = driver.find_element_by_id("username")
        password_el = driver.find_element_by_id("password")
        username_el.send_keys(username)
        password_el.send_keys(password)
        driver.find_element_by_name("submit").click()
        time.sleep(5)
        # blijkbaar niet nodig
        # self.driver.find_element_by_xpath("//input[@type='submit']").click()
        # time.sleep(10)
        # self.driver.find_element_by_xpath("//input[@type='submit']").click()
        # time.sleep(10)
        cookies = driver.get_cookies()
        time.sleep(5)
        driver.close()
        time.sleep(5)
        return cookies

    def check_login(self, response):
        """Check if we are successfully logged in."""
        # if "SOWISO B.V." in response.body:
        if "log uit" in response.text:
            logging.info("Successfully logged in")

            # Now the crawling can begin..
            return self.initialized()
        else:
            logging.info("Failed")
            # Something went wrong, we couldn't log in, so nothing happens.

    # Save the zip file with its name in a folder with the students name
    def parse_item(self, response):
        folder = response.meta.get('student_name')



        # Get names and concat them
        filename = response.url.split("/")[-2] + '_' + \
                    response.url.split("/")[-1]
        assignment = response.meta.get('assignment')
        folder_path = os.path.join(self.save_dir, assignment, folder)
        file_path = os.path.join(folder_path, filename)
        logging.info("about to save file with url %s to %s",
                     response.url, file_path)

        # Make folders and file
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        with open(file_path, "wb") as f:
            f.write(response.body)

    # Parse the name and zip file url on the page
    def parse_solution_page(self, response):
        assignment = response.meta.get('assignment')
        student_name = slugify(
                response.xpath('//small/text()').extract_first())
        url = self.login_page + response.xpath(
                #'//a[contains(@href, "files")]/@href').extract_first()
                '//a[contains(@href, "files")]/@href').extract()[1]
        logging.info("about to parse solution of %s by %s with url %s",
                     assignment, student_name, url)

        # meta is to send name through, cannot have kwargs**
        # Check if name is not empty
        if student_name and url:
            # Calls parse_item
            yield Request(url=url, cookies=self.cookies,
                          callback=self.parse_item,
                          meta={'student_name': student_name,
                                'assignment': assignment})

    # Parse the long list in which you cannot download all (sigh)
    def parse(self, response):
        # inspect_response(response, self)

        page_name = slugify(response.xpath('//h3/text()').extract_first())
        logging.info("starting to parse solutions of %s with url %s",
                     page_name, response.url)
        for numobj in response.xpath('//td[contains(@id, "test_id")]/@id'):
            num = numobj.extract()[-6:]
            url = self.login_page + '/teacher/grade_test/' + num

            # Calls parse_solution_page
            yield Request(url=url, cookies=self.cookies,
                          callback=self.parse_solution_page,
                          meta={'assignment': page_name})
