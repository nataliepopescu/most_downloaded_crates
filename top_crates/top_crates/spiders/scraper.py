import scrapy
from scrapy import Request
import json
import re
import subprocess

class CratesSpider(scrapy.Spider):
    name = 'top'
    per_page = 50
    total_page = 4

    def start_requests(self):
        url = 'https://crates.io/api/v1/crates?page={page}&per_page={per_page}&sort=downloads'
        for page in range(self.total_page):
            yield Request.from_curl(
                "curl " + url.format(page=page+1, per_page=self.per_page),
                callback=self.parse)


    def parse(self, response):
        data = json.loads(response.body.decode('utf-8'))
        filename = "crates.out"

        with open(filename, 'a') as f:
            for crate in data['crates']:
                if 'name' not in crate or 'newest_version' not in crate:
                    print("Error: invalid json for crate " + crate['id'])
                    return None
                f.write("    {\n")
                f.write("      \"Package\": {\n")
                f.write("        \"name\": \"" + crate['name'] + "\",\n")
                f.write("        \"version\": \"" + crate['newest_version'] + "\"\n")
                f.write("      }\n")
                f.write("    },\n")
