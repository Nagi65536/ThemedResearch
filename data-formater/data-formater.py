import glob

files = glob.glob("logs/*")

for file in files:
    datum = []
    range_list = []

    with open(file) as f:
        datum_list = f.read().split('\n')

    for i in range(len(datum_list)):
        if i % 2 == 0 and i+2 <= len(datum_list):
            range_list.append(datum_list[i])
            datum.append([datum_list[i], datum_list[i+1]])

    range_list = list(set(range_list))

    input_data = ''
    for range_ in range_list:
        input_data += range_ + '\n'
        for data in datum:
            if range_ == data[0]:
                input_data += data[1] + '\n'

    with open(f'./output-{file}', 'w') as f:
        f.write(input_data)
