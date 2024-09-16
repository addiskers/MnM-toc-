import scrapy
import os
from w3lib.html import remove_tags
import re
from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI')
def normalize_json(data):
        return [unicodedata.normalize('NFKD', item) if isinstance(item, str) else item for item in data]

class DaSpider(scrapy.Spider):
    name = 'da'
    start_urls = ['https://www.marketsandmarkets.com/Market-Reports/mobile-robots-market-43703276.html']

    # MongoDB connection setup
    client = MongoClient(MONGO_URI)
    db = client['MnMdata']
    collection = db['structured_headings']
    
    def __init__(self, url=None, *args, **kwargs):
        super(DaSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
            
    def parse(self, response):
        content = response.css('div.tab-pane#tab_default_2').xpath('.//text()').getall()

        if content:
            cleaned_content = [remove_tags(line).strip() for line in content]
            structured_content = [line for line in cleaned_content if line and not line.lower().startswith(('figure', 'table'))]
            structured_content = normalize_json(structured_content)
            # Filter the headings using the defined methods
            filtered_headings = self.filter_headings(self.parse_headings(structured_content))
            
            # Structure the filtered data into chapters and sub-sections
            structured_data = self.structure_data(filtered_headings)

            # Prepare the document for MongoDB
            document = {"chapters": []}
            for chapter, content in structured_data.items():
                document["chapters"].append({
                    "chapter": content["chapter"],
                    "sub_sections": content["sub_sections"]
                })

            # Insert the structured document into MongoDB
            self.collection.insert_one(document)
            self.log("Data inserted successfully into MongoDB")

            # Verify insertion
            inserted_doc = self.collection.find_one()
            self.log(f"Inserted document: {inserted_doc}")
        else:
            self.log('Failed to retrieve content.')

    def parse_headings(self, data):
        headings = {}
        pattern = re.compile(r'^(\d+(\.\d+)*)')  # Pattern to match heading numbers
        
        for entry in data:
            match = pattern.match(entry)
            if match:
                key = match.group(1)
                headings[key] = entry
        
        return headings

    def get_sibling_count(self, heading, headings):
        parts = heading.split('.')
        base = '.'.join(parts[:-1]) if len(parts) > 1 else ''
        count = 0
        for i in range(1, 100):
            sibling = base + '.' + str(i) if base else str(i)
            if sibling in headings:
                count += 1
            if count >= 2:
                return count
        return count

    def should_print(self, heading, headings):
        sibling_count = self.get_sibling_count(heading, headings)
        return sibling_count >= 2

    def filter_headings(self, headings):
        filtered = []
        keys = sorted(headings.keys(), key=lambda x: list(map(int, x.split('.'))))
        
        i = 0
        while i < len(keys):
            current = keys[i]
            if self.should_print(current, headings):
                filtered.append(headings[current])
                i += 1
                while i < len(keys) and keys[i].startswith(current + '.'):
                    sub_heading = keys[i]
                    if self.should_print(sub_heading, headings):
                        filtered.append(headings[sub_heading])
                    i += 1
            else:
                i += 1
        
        return filtered

    def structure_data(self, data):
        structured_data = {}
        for item in data:
            parts = item.split(" ")
            chapter = parts[0].split(".")[0]

            if chapter not in structured_data:
                structured_data[chapter] = {"chapter": item, "sub_sections": []}
            else:
                structured_data[chapter]["sub_sections"].append(item)

        return structured_data
