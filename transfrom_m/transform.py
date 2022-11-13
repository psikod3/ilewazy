import pandas as pd
import json

# options = {'display.max_columns': None, 'display.width': None,'display.max_rows': None, 'display.max_colwidth': 100}
# [pd.set_option(option, value) for option, value in options.items()]

with open('../mojscrapy/scrap_results_decoded.json', encoding='utf-8') as f:
    results_list = json.load(f)

# print(results_list)
final_dict = {}

for item in results_list:
    for key,value in item.items():
        value['Skład'] = value.pop(key)
        temp = list(value.keys())
        temp2 = [item for item in temp if 'na zdjęciu' in item]
        value['Porcjax'] = value.pop(temp2[0])
        dict_temp = {}
        for number, grams in value['100g'].items():
            dict_temp[value['Skład'][number]] = grams
        value['100 g'] = dict_temp
        dict_temp2 = {}
        for number, grams in value['Porcjax'].items():
            dict_temp2[value['Skład'][number]] = grams
        value['Porcja'] = dict_temp2
        [value.pop(useless_key) for useless_key in ['100g', 'Skład', 'Porcjax']]
    final_dict.update(item)

# print(final_dict)

unnested_dict = {}
for outerKey, innerDict in final_dict.items():
    for innerKey, innerDict2 in innerDict.items():
        for innerKey2, values in innerDict2.items():
            unnested_dict[(outerKey, innerKey, innerKey2)] = values
# print(unnested_dict)

df = pd.DataFrame(unnested_dict, index=[0])
df_t = df.transpose()
print(df_t.head(20))


# df = pd.DataFrame.from_dict(final_dict, orient='index')
# print(df.head())
# df['Skład'] = df['100 g'].map(lambda x: list(x.keys()))
# df = df.explode('Skład')
# print(df.head())
