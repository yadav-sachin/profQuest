import jsonlines
import json
import os.path
from scrapy import Selector 
country = "britain"
# country = input().strip()
# list_file = open("data/input_lists/{}_completed.txt".format(country), "r")
# institute_list = set(list_file.read().splitlines())
# institute_count = {}

with jsonlines.open('oup_{}.jl'.format(country)) as reader:
    max_count, curr_count = 10, 1
    for obj in reader:
        if os.path.isfile("data/output_data/{}/{}.html".format(country, obj['user'])):
            with open("data/output_data/{}/{}.html".format(country, obj['user']), "r" , encoding = "utf-8-sig") as file:
                page = file.read()
                data = Selector(text=str(page))
                # Google Scholar Page Link
                obj['scholarPage'] = "https://scholar.google.co.in/citations?user={}&hl=en".format(obj['user'])
                # Profile Pic Link
                obj['imgLink'] = "Not Found"
                imgLink = data.xpath("//div[@id='gsc_prf_pua']//img/@src").get()
                if imgLink:
                    if imgLink.find("avatar_scholar_128") >= 0:
                        imgLink = "https://scholar.google.co.in" + imgLink
                    obj['imgLink'] = imgLink
                # verifiedEmail True/False
                obj['verifiedEmail'] = False
                verifiedEmail = data.xpath("//div[@id='gsc_prf_ivh']/text()").re(r".*Verified email.*")
                if verifiedEmail:
                    obj['verifiedEmail'] = True
                # Subject topics
                obj['subjects'] = data.xpath("//div[@id='gsc_prf_int']//a/text()").getall()
                # Citations over the Years
                years_list = data.xpath("//span[contains(@class, 'gsc_g_t')]/text()").getall()
                z_index_list = list(map(int, data.xpath("//a[contains(@class, 'gsc_g_a')]/@style").re(r".*z-index:(.*)")))
                year_citations_list = data.xpath("//span[contains(@class, 'gsc_g_al')]/text()").getall()
                year_citations_list = list(map(int, year_citations_list))
                json_citations_list = []
                if not z_index_list:
                    #If the user has no citations yet
                    continue
                max_z_index = max(z_index_list)
                idx2 = 0
                for idx, year in enumerate(years_list):
                    z_index = max_z_index - idx
                    if z_index in z_index_list:
                        json_citations_list.append( json.dumps({"year": int(years_list[idx]), "citations": int(year_citations_list[idx2])}) )
                        idx2 += 1
                    else:
                        json_citations_list.append( json.dumps({"year": int(years_list[idx]), "citations": 0}) )
                obj['yearCitations'] = json_citations_list
                # all Citations
                obj['citationsAll'] = data.xpath("(//table[@id='gsc_rsb_st']//tbody//td[contains(@class,'gsc_rsb_std')]/text())[1]").get()
                ## Citations since 2016
                obj['citations2016'] = data.xpath("(//table[@id='gsc_rsb_st']//tbody//td[contains(@class,'gsc_rsb_std')]/text())[2]").get()
                # h-index All
                obj['h-indexAll'] = data.xpath("(//table[@id='gsc_rsb_st']//tbody//td[contains(@class,'gsc_rsb_std')]/text())[3]").get()
                # h-index since 2016
                obj['h-index2016'] = data.xpath("(//table[@id='gsc_rsb_st']//tbody//td[contains(@class,'gsc_rsb_std')]/text())[4]").get()
                # i10-index All
                obj['i10-indexAll'] = data.xpath("(//table[@id='gsc_rsb_st']//tbody//td[contains(@class,'gsc_rsb_std')]/text())[5]").get()
                # i10-index since 2016
                obj['i10-index2016'] = data.xpath("(//table[@id='gsc_rsb_st']//tbody//td[contains(@class,'gsc_rsb_std')]/text())[6]").get()
                # papers
                json_paper_list = []
                papers = data.xpath("//tbody[@id='gsc_a_b']//tr")
                # print(papers)
                for paper in papers:
                    title = paper.xpath("(.//td)[1]//a/text()").get()
                    authors = paper.xpath("((.//td)[1]//div)[1]/text()").get()
                    conference = paper.xpath("((.//td)[1]//div)[2]//text()").get()
                    citations = paper.xpath("(.//td)[2]//a/text()").get()
                    if not citations:
                        citations = 0
                    citations = int(citations)
                    year = paper.xpath("(.//td)[3]//span/text()").get()
                    if year:
                        year = int(year)
                        paper_dict = {"title":title, "authors":authors, "conference":conference, "citations":citations, "year":year}
                        json_paper_list.append(paper_dict)
                obj['papers'] = json_paper_list
                # print(papers)
                json_obj = json.dumps(obj)
                print(json_obj)
                # if curr_count == max_count:
                #     break
                curr_count += 1
