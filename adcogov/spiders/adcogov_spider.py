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

    
            
    def validate(self, val):
        try:
            return val[0].strip()
        except:
            return ""

    def clean(self, val):
        return [v.strip() for v in val if v.strip() != ""]



