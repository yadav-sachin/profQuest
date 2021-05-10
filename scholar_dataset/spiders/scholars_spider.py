import scrapy
import os
from scrapy.linkextractors import LinkExtractor
from urllib.parse import parse_qs, urlparse
from w3lib.url import add_or_replace_parameters
from scrapy.exceptions import CloseSpider
import re 

# The max number of profiles for the first entry insitute = 400
# The number of profiles extracted for each institute decreases as we move to throught the institute entries
# The institutes list is expected to be in order of some ranking
max_persons_per_institute = 400
# Keep track of the completed institutes and the ones whose results were not found
institute_remaining_count = {}
institute_file_completed_list = []
institute_found_list = []

class ScholarsSpider(scrapy.Spider):
    name = 'scholars'
    # Read the input files, check the already completed ones and start the process for each record
    def start_requests(self):
        institutes_namelist = ["iit bombay", "iit delhi"]
        if not os.path.isdir("data/output_data/{}".format(self.country)):
            os.makedirs("data/output_data/{}".format(self.country))

        institute_file_list = open('data/input_lists/{}.txt'.format(self.country), 'r')
        institutes_namelist = institute_file_list.read().splitlines()  #remove the :10 in deployment
        institutes_namelist = [name.strip() for name in institutes_namelist]
        for index, name in enumerate(institutes_namelist):
            institute_remaining_count[name] = max_persons_per_institute - 2 * index

        if os.path.isfile('data/input_lists/{}_completed.txt'.format(self.country)):
            with open('data/input_lists/{}_completed.txt'.format(self.country), 'r') as institute_file_completed_file:
                institute_file_completed_list = institute_file_completed_file.read().splitlines()
        else:
            open('data/input_lists/{}_completed.txt'.format(self.country), 'a').close()
            institute_file_completed_list = []


        if os.path.isfile('data/input_lists/{}_not_found.txt'.format(self.country)):
            with open('data/input_lists/{}_not_found.txt'.format(self.country), 'r') as institute_file_not_found_file:
                    institute_file_completed_list.extend(institute_file_not_found_file.read().splitlines())

        for name in institute_file_completed_list:
            institute_remaining_count[name] = 0
            if name in institutes_namelist:
                institutes_namelist.remove(name)

        institutes_namelist = institutes_namelist[::-1]
        institute_termlist = ["+".join(name.strip().split()) for name in institutes_namelist]
        start_urls = ['https://www.google.com/search?q={}+{}+google+scholar&hl=en'.format(term, self.country) for term in institute_termlist]
        for index, url in enumerate(start_urls):
            yield scrapy.Request(url, meta={'institute_name': institutes_namelist[index].strip()})

    # Currently at Google Search result page, need to go to the first google search result
    # https://www.google.com/search?q=iit+bombay+google+scholar
    def parse(self, response):
        institute_name = response.meta['institute_name']
        page_links = response.xpath("//a[contains(@href, 'citations') and contains(@href, 'user')  and not(contains(@href, 'cache')) ]/@href").getall()
        max_try_count = min(len(page_links), 5)
        try_count = 1
        if not page_links:
            if institute_name not in institute_found_list:
                    f = open('data/input_lists/{}_not_found.txt'.format(self.country), 'a')
                    f.write(institute_name + "\n")
                    f.close()
        for link in page_links:
            yield response.follow(link, self.parse_scholar_page_lvl1, meta={'institute_name': response.meta['institute_name'],'try_count': try_count})
            if try_count == max_try_count:
                if institute_name not in institute_found_list:
                    f = open('data/input_lists/{}_not_found.txt'.format(self.country), 'a')
                    f.write(institute_name + "\n")
                    f.close()
                break
            try_count = try_count + 1

    # Currently at the faculty page, came here via google search, need to go to the organisation page
    # https://scholar.google.com/citations?user=5y4YmFcAAAAJ&hl=en
    def parse_scholar_page_lvl1(self, response):
        institute_name = response.meta['institute_name']
        org_link = response.xpath("//a[contains(@href, 'org') and contains(@class, 'gsc_prf_ila') and contains(@href, 'citations')]/@href").get()
        if org_link:
            orgID = parse_qs(urlparse(org_link).query)['org'][0]
            if institute_name not in institute_found_list:
                institute_found_list.append(institute_name)
            yield response.follow(org_link, self.parse_institute_next_page_lvl2, meta={'institute_name': response.meta['institute_name'], 'orgID': orgID})

    # Currently at the institute page, which has the list of the faculties
    def parse_institute_next_page_lvl2(self, response):
        # https://scholar.google.com/citations?view_op=view_org&hl=en&org=15559271020991466530&after_author=s5UKAF3A__8J
        institute_name = response.meta['institute_name']
        person_links = response.xpath("//h3[contains(@class, 'gs_ai_name')]//a[contains(@href, 'citations') and contains(@href, 'user')]/@href").getall()
        for link in person_links:
            if institute_remaining_count[institute_name] > 0:
                link = add_or_replace_parameters(link, {"hl": "en"})
                yield response.follow(link, self.download_person_page, meta={'institute_name': institute_name, 'orgID': response.meta['orgID']})
                institute_remaining_count[institute_name] -= 1
            else:
                print(institute_name, institute_remaining_count[institute_name])
                if institute_name not in institute_file_completed_list:
                    f = open('data/input_lists/{}_completed.txt'.format(self.country), 'a')
                    f.write(institute_name + "\n")
                    f.close()
                    institute_file_completed_list.append(institute_name)
        
        next_page_after_authors =  response.css('button.gs_btnPR').xpath(".//@onclick").re(r"window.location='.*after_author\\x3d(.*)\\.*\\.*'")
        if next_page_after_authors and institute_remaining_count[institute_name] > 0:
            next_page_after_author = next_page_after_authors[0]
            next_page_link = add_or_replace_parameters(response.url, {"after_author": next_page_after_author})
            yield response.follow(next_page_link , self.parse_institute_next_page_lvl2, meta={'institute_name': response.meta['institute_name'], 'orgID': response.meta['orgID']})
        else:
            print(institute_name, institute_remaining_count[institute_name])
            if institute_name not in institute_file_completed_list:
                f = open('data/input_lists/{}_completed.txt'.format(self.country), 'a')
                f.write(institute_name + "\n")
                f.close()
                institute_file_completed_list.append(institute_name)

    # On a person's page, ready to download the HTML file and related data in 
    def download_person_page(self, response):
        userID = parse_qs(urlparse(response.url).query)['user'][0]
        filename = f'data/output_data/{self.country}/{userID}.html'
        org_link = response.css("a.gsc_prf_ila::attr(href)").get()
        orgID = parse_qs(urlparse(org_link).query)['org'][0]
        name = response.css("div#gsc_prf_in::text").get()
        if not name:
            name = "Not Found"
        homepage = response.css("div#gsc_prf_ivh").xpath("./a/@href").get()
        if not homepage:
            homepage = "Not Found"
        yield {
            'country': self.country,
            'org': response.meta['orgID'],
            'institute': response.meta['institute_name'],
            'name': name,
            'user': userID,
            'homepage': homepage,
        }
        with open(filename, 'wb') as f:
            html_data = re.sub(b"<style>[.\S\s]*?</style>", b"", response.body, re.DOTALL)
            html_data = re.sub(b"<script>[.\S\s]*?/script>", b"", html_data, re.DOTALL)
            f.write(html_data)
