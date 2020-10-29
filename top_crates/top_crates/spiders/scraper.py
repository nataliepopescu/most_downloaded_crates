import scrapy
from scrapy import Request
import json
import re
import os
import subprocess

class CratesSpider(scrapy.Spider):
    name = 'top'
    per_page = 50
    total_page = 10
    filename = "crates.out"
    count = 0

    def start_requests(self):
        url = 'https://crates.io/api/v1/crates?page={page}&per_page={per_page}&sort=downloads'
        def write_time():
            with open(self.filename, 'w') as f:
                f.write("{\n")
                f.write("  \"creation_date\": {\n")
                secs = subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True)
                f.write("    \"secs_since_epoch\": " + str(secs.stdout[:-1]) + ",\n")
                nanos = subprocess.run(["date", "+%N"], stdout=subprocess.PIPE, text=True)
                f.write("    \"nanos_since_epoch\": " + str(nanos.stdout[:-1]) + ",\n")
                f.write("  },\n")
                f.write("  \"crates\": [")

        write_time()
        for page in range(self.total_page):
            yield Request.from_curl(
                "curl " + url.format(page=page+1, per_page=self.per_page),
                callback=self.parse)


    def parse(self, response):
        data = json.loads(response.body.decode('utf-8'))

        with open(self.filename, 'a') as f:
            for crate in data['crates']:
                self.count += 1
                if 'name' not in crate or 'newest_version' not in crate:
                    print("Error: invalid json for crate " + crate['id'])
                    return None
                f.write("    {\n")
                f.write("      \"Package\": {\n")
                f.write("        \"name\": \"" + crate['name'] + "\",\n")
                f.write("        \"version\": \"" + crate['newest_version'] + "\"\n")
                f.write("      }\n")
                if self.count == (self.per_page * self.total_page):
                    f.write("    }\n")
                    f.write("  ]\n")
                    f.write("}\n")
                else:
                    f.write("    },\n")
