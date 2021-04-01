from os import listdir
from os.path import isfile, join
import jsonlines
country = "india"
# country = input()
html_files = [f for f in listdir("data/output_data/{}".format(country)) if isfile(join("data/output_data/{}".format(country), f))]
html_file_names = [name.split('.')[0] for name in html_files]


with jsonlines.open('oup_{}.jl'.format(country)) as reader:
    for obj in reader:
        if obj['user'] in html_file_names:
            html_file_names.remove(obj['user'])

print(len(html_file_names))
