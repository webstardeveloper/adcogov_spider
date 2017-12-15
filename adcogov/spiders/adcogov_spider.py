import scrapy

from selenium import webdriver
from selenium.webdriver.support.ui import Select
# from pyvirtualdisplay import Display

from lxml import html
import time
import json

from xlutils.copy import copy
import xlrd

class AdcogovSpider(scrapy.Spider):
    name = "adcogov"
    target = "http://recording.adcogov.org/landmarkweb"

    ids = []

    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.read_ids()

    def read_ids(self):
        self.rb = xlrd.open_workbook("data.xlsx")
        self.wb = copy(self.rb)

        ws = self.rb.sheet_by_index(0)
        for row in range(1, ws.nrows):
            try:
                self.ids.append(int(ws.cell(row, 0).value))
            except:
                pass

        print self.ids

    def start_requests(self):
        self.driver.get(self.target)
        self.driver.find_element_by_xpath("//a[@title='Go to Instrument Search.']").click()
        time.sleep(2)
        self.driver.find_element_by_xpath("//a[@id='idAcceptYes']").click()
        time.sleep(2)

        for idx in range(0, len(self.ids)):
            self.driver.find_element_by_xpath("//input[@id='instrumentNumber']").send_keys(str(self.ids[idx]))
            Select(self.driver.find_element_by_id('matchType-InstrumentNumber')).select_by_value('2')
            self.driver.find_element_by_xpath("//a[@id='submit-InstrumentNumber']").click()
            time.sleep(3)

            self.driver.find_element_by_xpath("//table[@id='resultsTable']/tbody/tr[1]").click()
            time.sleep(10)
            res = self.parse_data()
            print json.dumps(res, indent=4)
            break

        yield scrapy.Request(url='https://sports.ladbrokes.com/en-gb/bet-in-play/', callback=self.parse)

    def parse_data(self):
        source = self.driver.page_source
        tree = html.fromstring(source)

        attributes = tree.xpath("//table[@style='width: 100%']/tbody/tr")
        item = dict()
        image_path_list = []
        for attr in attributes:
            key = self.validate(attr.xpath("./td[1]/label/text()"))
            if key == "":
                continue
            if key == "Doc Links":
                value = "; ".join(self.clean(attr.xpath("./td[2]//a/text()")))
            else:
                value = "; ".join(self.clean(attr.xpath("./td[2]/text()")))

            item[key] = value

        image_path_temp = self.validate(tree.xpath("//img[@id='documentImageInner']/@src"))
        template = image_path_temp.split("pageNum=0")
        image_path_list.append(image_path_temp)
        if "Number of Pages" in item and int(item['Number of Pages']) > 1:
            for idx in range(1, int(item['Number of Pages'])):
                image_path_list.append(("pageNum=%d" % idx).join(template) )

        return [item, image_path_list]
            
    def validate(self, val):
        try:
            return val[0].strip()
        except:
            return ""

    def clean(self, val):
        return [v.strip() for v in val if v.strip() != ""]



