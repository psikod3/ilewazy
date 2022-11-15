import pandas as pd
import json

# options = {'display.max_columns': None, 'display.width': None,'display.max_rows': None, 'display.max_colwidth': 100}
# [pd.set_option(option, value) for option, value in options.items()]

with open('../mojscrapy/scrap_results_decoded.json', encoding='utf-8') as f:
    results_list = json.load(f)

# reorganizing table
final_dict = {}

for item in results_list:
    for key, value in item.items():
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

# moving all keys to tuple, so df will have easy time adding them to multiindex
#   on the 1st level of index will be product name
#   2nd - portion size: 100 g or default
#   3rd - composition (Skład)
unnested_dict = {}
for outerKey, innerDict in final_dict.items():
    for innerKey, innerDict2 in innerDict.items():
        for innerKey2, values in innerDict2.items():
            unnested_dict[(outerKey, innerKey, innerKey2)] = values

# 1) removing letters and spaces from values, and changing , to .
# 2) recreating unnested_dict with cleaned values
value_list = list(unnested_dict.values())
value_list_cleaned = []
for item in value_list:
    str(item)
    item_cleaned = item.replace(" kcal", "").replace(" g", "").replace(",", ".")
    value_list_cleaned.append(item_cleaned)

unnested_dict_cleaned = {}
count = 0
for key, value in unnested_dict.items():
    unnested_dict_cleaned[key] = value_list_cleaned[count]
    count = count + 1

# print(unnested_dict)
# print(unnested_dict_cleaned)

# creating multiindex dataframe
df = pd.DataFrame(unnested_dict_cleaned, index=[0])
ilewazy_df = df.transpose()  # looks better
# print(ilewazy_df.head(20))
