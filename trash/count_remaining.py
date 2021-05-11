import jsonlines
list_file = open("data/input_lists/india_completed.txt", "r")
institute_list = set(list_file.read().splitlines())
institute_count = {}

for institute in institute_list:
    institute_count[institute] = 0
oup_data = []

with jsonlines.open('oup4.jl') as reader:
    for obj in reader:
        if obj['institute'] in institute_count:
            institute_count[obj['institute']] += 1
        else: 
            institute_count[obj['institute']] = 1

for index, institute in enumerate(institute_list):
    required = 400 - 2 * index
    count = institute_count[institute]
    remaining = required - count
    if remaining < 40:
        # print(institute, "Required :", required, "Count: ", count)
        print(institute)
