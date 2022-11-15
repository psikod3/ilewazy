import pandas as pd
import json

# options = {'display.max_columns': None, 'display.width': None,'display.max_rows': None, 'display.max_colwidth': 100}
# [pd.set_option(option, value) for option, value in options.items()]

with open('../mojscrapy/scrap_results_decoded_fixed.json', encoding='utf-8') as f:
    results_list = json.load(f)

# duplicate check
# print(len(results_list))
# x=[list(item.keys())[0] for item in results_list]
# y=[item for item in x if x.count(item) >=2]
# print(y)
# print(len(set(x)))
# input()

# reorganizing table
final_dict = {}
na_zdjeciu = []  # gonna need this for later
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
# value_list = list(unnested_dict.values())
# value_list_cleaned = []
# for item in value_list:
#     str(item)
#     item_cleaned = item.replace(" kcal", "").replace(" g", "").replace(",", ".")
#     value_list_cleaned.append(item_cleaned)
#
# unnested_dict_cleaned = {}
# count = 0
# for key, value in unnested_dict.items():
#     unnested_dict_cleaned[key] = value_list_cleaned[count]
#     count = count + 1

# print(unnested_dict)
# print(unnested_dict_cleaned)
# print('unnested_dict_cleaned', len(unnested_dict_cleaned))

# print('dl na zdj', len(na_zdjeciu))
# na_zdjeciu_cleaned = []
# for item in na_zdjeciu:
#     item_cleaned = item.replace("['na zdjęciu (", "").replace(" g)']", "").replace(",", ".")
#     na_zdjeciu_cleaned.append(item_cleaned)
# # print(na_zdjeciu)
# # print(na_zdjeciu_cleaned)
# print('dl na zdj_c', len(na_zdjeciu_cleaned))  # dl na zdj_c 5614 OK!

# creating (multiindex) dataframe from dict with tuples as keys
mdf = pd.DataFrame(unnested_dict_cleaned, index=[0])
mdf_t = mdf.transpose()  # looks better
# mdf_t.rename(columns={0: 'kcal / g'}, inplace=True)

df = mdf_t.reset_index()  # converting multiindex to normal df

# reorganizing df
df['id'] = range(67968)  # setting up unique id for merge
# print(df.head(10))

na_zdjeciu_df = df[(df['level_1'] == "100 g") & (df['level_2'] == "Błonnik")]  # dl na zdj_df 5607
print(na_zdjeciu_df)
print('dl na zdj_df', len(na_zdjeciu_df.index))
# na_zdjeciu_df['Porcja (g)'] = na_zdjeciu_cleaned
# print(na_zdjeciu_df.head(10))

# splitting 100 g related data from 0 column into GRAMY and KCAL
stog_sklad = df[(df['level_1'] == "100 g") & (df['level_2'] != "Energia")]
stog_sklad.rename(columns={0: "100 g (skład)"}, inplace=True)
stog_sklad.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

stog_en = df[(df['level_1'] == "100 g") & (df['level_2'] == "Energia")]
stog_en.rename(columns={0: "100 g (kcal)"}, inplace=True)
stog_en.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
# print(stog_en.head(10))

df2 = df.merge(stog_sklad, on='id', how='outer')
# print(df2.head(20))
# print('df2', len(df2.index))
df3 = df2.merge(stog_en, on='id', how='outer')
# print(df3.head(20))
# print('df3', len(df3.index))

# splitting of the 100g column

# df2.rename(columns={"level_1_y": "a", "B": "c"})

# print('stog:', len(stog_eng.index))
# print(stog_eng.head(10))
#
# porcja = df[df['level_1'] == "Porcja"]
# print('porcja:', len(porcja.index))
# energia = df[df['level_2'] == "Energia"]
# print('energia:', len(energia.index))
# sklad = df[df['level_2'] != "Energia"]
# print('sklad:', len(sklad.index))
# print('df:', len(df.index))

# df3 = df2.merge(porcja, on='id', how='outer')

# ilewazy_df.drop(columns=['level_1', 'level_2', 0], inplace=True)

# df['100 g'] = df[df['level_1'] == "100 g"]

# print(sklad.head(10))
# print(df.head(20))
# print('df:', len(df.index))
# print(df3.head(20))
# print('df3', len(df3.index))
# print(len(ilewazy_df.index))