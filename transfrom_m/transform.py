import pandas as pd
import json

# options = {'display.max_columns': None, 'display.width': None,'display.max_rows': None, 'display.max_colwidth': 100}
# [pd.set_option(option, value) for option, value in options.items()]

<<<<<<< Updated upstream
=======
# # make pycharm console view wider df
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 12)

>>>>>>> Stashed changes
with open('../mojscrapy/scrap_results_decoded_fixed.json', encoding='utf-8') as f:
    results_list = json.load(f)  # results from file are actually a list of dicts

# duplicate check
# print(len(results_list))
# x=[list(item.keys())[0] for item in results_list]
# y=[item for item in x if x.count(item) >=2]
# print(y)
# print(len(set(x)))
# input()

# reorganizing dict
organized_dict = {}
for dictionary in results_list:
    for name_1, name_2 in dictionary.items():

        name_2['Skład'] = name_2.pop(name_1)  # need replace name_2 ind 2nd lvl dict with key with one name
        key_list = list(name_2.keys())  # temp list of keys
        key_list_2 = []
        for item in key_list:
            if 'na zdjęciu' in item:
                key_list_2.append(item)
                # list comp: key_list_2 = [item for item in key_list if 'na zdjęciu' in item]
        name_2['Porcja'] = name_2.pop(key_list_2[0])  # replacing "blah na zdjeciu" in 2nd dict with key with one name

        dict_temp = {}  # preparation to remove pointless keys in dicts (i.e. "0" , "1", "2") called later indexes
        for index, kcal_g in name_2['100g'].items():
            dict_temp[name_2['Skład'][index]] = kcal_g  # makes dict with keys from values of name_2['Skład'] and values
                                                        # from name_2['100g']
        name_2['nowe 100g'] = dict_temp  # adding cleaned dict

        dict_temp_2 = {}  # again
        for index, kcal_g in name_2['Porcja'].items():
            dict_temp_2[name_2['Skład'][index]] = kcal_g
        name_2['nowa Porcja'] = dict_temp_2

        [name_2.pop(useless_key) for useless_key in ['100g', 'Skład', 'Porcja']]  # removing useless dicts

        name_2['nowe 100g']['Wielkość porcji'] = key_list_2[0] # saving 'na zdjęciu (X g)' for df
        name_2['nowa Porcja']['Wielkość porcji'] = key_list_2[0]

    organized_dict.update(dictionary)
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes

# moving all keys to tuple, so df will have easy time adding them to multiindex
#   on the 1st level of index will be product name
#   2nd - portion size: 100 g or default
#   3rd - composition (Skład)
unnested_dict = {}
for outerKey, innerDict in organized_dict.items():
    for innerKey, innerDict2 in innerDict.items():
        for innerKey2, values in innerDict2.items():
            unnested_dict[(outerKey, innerKey, innerKey2)] = values

<<<<<<< Updated upstream

# creating (multiindex) dataframe from dict with tuples as keys
mdf = pd.DataFrame(unnested_dict, index=[0])
mdf_t = mdf.transpose()  # looks better
# mdf_t.rename(columns={0: 'kcal / g'}, inplace=True)

pre_df = mdf_t.reset_index()  # converting multiindex to normal df
df = pre_df.rename(columns={0: "Dane"})
df.index.name = 'idx'

print(df.head(20))
=======
mdf = pd.DataFrame(unnested_dict, index=[0])  # creating (multiindex) dataframe from dict with tuples as keys
mdf_transposed = mdf.transpose()  # looks better
>>>>>>> Stashed changes

energia = df[(df['level_2'] == "Energia")]
energia2 = energia.rename(columns={'Dane': "Energia (kcal)"})  # new df cause inplace=True throws warning
energia2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

bialko = df[(df['level_2'] == "Białko")]
bialko2 = bialko.rename(columns={'Dane': "Białko (g)"})
bialko2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

tluszcz = df[(df['level_2'] == "Tłuszcz")]
tluszcz2 = tluszcz.rename(columns={'Dane': "Tłuszcz (g)"})
tluszcz2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

tluszcz_nasyc = df[(df['level_2'] == "Kwasy tłuszczowe nasycone")]
tluszcz_nasyc2 = tluszcz_nasyc.rename(columns={'Dane': "Kwasy tłuszczowe nasycone (g)"})
tluszcz_nasyc2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

wegle = df[(df['level_2'] == "Węglowodany")]
wegle2 = wegle.rename(columns={'Dane': "Węglowodany (g)"})
wegle2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

cukry = df[(df['level_2'] == "Cukry proste")]
cukry2 = cukry.rename(columns={'Dane': "Cukry proste (g)"})
cukry2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

blonnik = df[(df['level_2'] == "Błonnik")]
blonnik2 = blonnik.rename(columns={'Dane': "Błonnik (g)"})
blonnik2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

blonnik = df[(df['level_2'] == "Sól")]
blonnik2 = blonnik.rename(columns={'Dane': "Błonnik (g)"})
blonnik2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)


df_en = df.merge(energia2, on='idx', how='outer')
df_en_b = df_en.merge(bialko2, on='idx', how='outer')
df_en_b_t = df_en_b.merge(tluszcz2, on='idx', how='outer')
df_en_b_t_tn = df_en_b_t.merge(tluszcz_nasyc2, on='idx', how='outer')
df_en_b_t_tn_w = df_en_b_t_tn.merge(wegle2, on='idx', how='outer')
df_en_b_t_tn_w_c = df_en_b_t_tn_w.merge(cukry2, on='idx', how='outer')
df_en_b_t_tn_w_c_b = df_en_b_t_tn_w_c.merge(blonnik2, on='idx', how='outer')

print(df_en_b_t_tn_w.head(16))



# len check
# print('df', len(df.index))
# print('df_en', len(df_en.index))

# df2.level_1 = df2.Dane.where(df2.level_2 == 'Wielkość porcji', df2.level_1)


# print(df2.head(20))



'''
# splitting 100 g related data from 0 column into GRAMY and KCAL
stog_sklad = df[(df['level_1'] == "nowe 100g") & (df['level_2'] != "Energia")]
stog_sklad_2 = stog_sklad.rename(columns={0: "100 g (skład)"})  # new df cause inplace=True throws warning
stog_sklad_2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)

stog_en = df[(df['level_1'] == "nowe 100g") & (df['level_2'] == "Energia")]
stog_en_2 = stog_en.rename(columns={0: "100 g (kcal)"})
stog_en_2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
# print(stog_en.head(10))

df2 = df.merge(stog_sklad_2, on='id', how='outer')
print(df2.head(20))
# print('df2', len(df2.index))
df3 = df2.merge(stog_en_2, on='id', how='outer')
print(df3.head(20))
# print('df3', len(df3.index)) '''

<<<<<<< Updated upstream
# elegancko ale lepiej zrobic by w level_1 (Porcja)  byly dwa wiersze: 100g oraz wartosc z na zdjeciu
# a bialko, wegle itd przeniesc na kolumny


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
=======
>>>>>>> Stashed changes
