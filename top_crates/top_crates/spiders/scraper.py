import scrapy
from scrapy import Request
import json
import re
import os
import subprocess

class CratesSpider(scrapy.Spider):
    name = 'top'
    per_page = 10 #50
    total_page = 1#4 #998
    filename = "CrateList.json"
    namelist = "sorted_crates.py"
    count = 0
    results = {}
    crates = []

    def start_requests(self):
        self.url = 'https://crates.io/api/v1/crates/bencher/reverse_dependencies?page={page}&per_page={per_page}'
        #self.url = 'https://crates.io/api/v1/crates?page={page}&per_page={per_page}&sort=downloads'
        def write_time():
            secs = subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True)
            nanos = subprocess.run(["date", "+%N"], stdout=subprocess.PIPE, text=True)
            self.results["creation_date"] = {}
            self.results["creation_date"]["secs_since_epoch"] = secs.stdout[:-1]
            self.results["creation_date"]["nanos_since_epoch"] = nanos.stdout[:-1]
            self.results["crates"] = []

        write_time()
        for page in range(self.total_page):
            yield Request.from_curl(
                "curl " + self.url.format(page=page+1, per_page=self.per_page),
                callback=self.parse)


    def parse(self, response):
        data = json.loads(response.body.decode('utf-8'))

        if 'reverse_dependencies' in self.url: 
            if 'versions' not in data:
                print("Error: invalid json")
                return None

            for crate in data['versions']:
                self.count += 1
                item = {"Package": {
                        "name": crate['crate'],
                        "version": crate['num'],
                        "downloads": crate['downloads']}}
                self.crates.append(item)
        else:
            if 'crates' not in data:    
                print("Error: invalid json")
                return None

            for crate in data['crates']:
                self.count += 1
                if 'name' not in crate or 'newest_version' not in crate:
                    print("Error: invalid json for crate " + crate['id'])
                    return None
                item = {"Package": {
                        "name": crate['name'], 
                        "version": crate['newest_version'],
                        "downloads": crate['downloads']}}
                self.crates.append(item)

        # only sort towards end
        if self.count > (self.per_page * (self.total_page - 1)):
            sorted_crates = sorted(self.crates, key=lambda d: d["Package"]["downloads"], reverse=True)
            self.results["crates"] = sorted_crates
            
            with open(self.filename, 'w') as f: 
                json.dump(self.results, f, indent=2)
            
            with open(self.namelist, 'w') as f:
                names = []
                for c in self.results["crates"]: 
                    names.append(c["Package"]["name"])

                f.write("sorted_crates = [\n")
                count = 1
                for n in names: 
                    f.write("  \"" + n + "\", # " + str(count) + "\n")
                    count += 1
                f.write("]")

