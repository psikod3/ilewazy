import pandas as pd
import json

# options = {'display.max_columns': None, 'display.width': None,'display.max_rows': None, 'display.max_colwidth': 100}
# [pd.set_option(option, value) for option, value in options.items()]

# # make pycharm console view wider df
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 12)

with open('../mojscrapy/scrap_results_decoded_fixed.json', encoding='utf-8') as f:
    results_list = json.load(f)  # results from file are actually a list of dicts

# # duplicate check
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

        dict_temp = {}  # preparation to remove pointless keys in dicts (i.e. "0" , "1", "2") called indexes below
        for index, kcal_g in name_2['100g'].items():
            dict_temp[name_2['Skład'][index]] = kcal_g  # makes dict with keys from values of name_2['Skład'] and values
            # from name_2['100g']
        name_2['nowe 100g'] = dict_temp  # adding cleaned dict

        dict_temp_2 = {}  # again
        for index, kcal_g in name_2['Porcja'].items():
            dict_temp_2[name_2['Skład'][index]] = kcal_g
        name_2['nowa Porcja'] = dict_temp_2

        [name_2.pop(useless_key) for useless_key in ['100g', 'Skład', 'Porcja']]  # removing useless dicts

        name_2['nowe 100g']['Wielkość porcji'] = key_list_2[0]  # saving 'na zdjęciu (X g)' for future df
        name_2['nowa Porcja']['Wielkość porcji'] = key_list_2[0]

    organized_dict.update(dictionary)

# moving all keys to tuple, so pandas will have easy time adding them to multiindex
#   on the 1st level of index will be product name
#   2nd - portion size: 100 g or default
#   3rd - composition (Skład)
unnested_dict = {}
for outerKey, innerDict in organized_dict.items():
    for innerKey, innerDict2 in innerDict.items():
        for innerKey2, values in innerDict2.items():
            unnested_dict[(outerKey, innerKey, innerKey2)] = values

mdf = pd.DataFrame(unnested_dict, index=[0])  # creating (multiindex) dataframe from dict with tuples as keys
mdf_transposed = mdf.transpose()  # looks better

# unstacks (transposes) most right index Skład (Energia, Białko, Tłuszcz ... Wielkość porcji ) to separate columns
# https://pandas.pydata.org/docs/user_guide/reshaping.html#reshaping-stacking
mdf_unstacked = mdf_transposed.unstack()

df = mdf_unstacked.reset_index()  # converts multiindex to normal df
df = df.droplevel(0, axis=1)  # removes useless top label from multi-label
df.columns = ['Produkt', 'Porcja', 'Białko', 'Błonnik', 'Cukry proste', 'Energia', 'Tłuszcze nasycone', 'Sól',
              'Tłuszcz', 'Kopiuj', 'Węglowodany']
df.Porcja = df.Kopiuj.where(df.Porcja == 'nowa Porcja', df.Porcja)  # copies values from Kopiuj ('na zdjęciu (62 g) etc)
df.drop(columns=['Kopiuj'], inplace=True)
df.set_index(['Produkt'], inplace=True)

# https://sparkbyexamples.com/pandas/pandas-change-position-of-a-column/
# wyczyścić dane, z - b.d. NaN oraz zmienić na liczby
# zminic nazwy na koncu Porcja = Porcja (g), Energia (kcal)

print(df.head(10))
# print(type(mdf))






# df2 = df.rename(columns={'level_0': "Produkt", 'level_1': "Porcja", 'Kwasy tłuszczowe nasycone': 'Tłuszcze nasycone', 'Wielkość porcji': 'Kopiuj'})
# df2.Porcja = df2.Kopiuj.where(df2.Porcja == 'nowa Porcja', df2.Porcja)

# df2.level_1 = df2.Dane.where(df2.level_2 == 'Wielkość porcji', df2.level_1)

# df.set_index()
# print(df2.head(20))


# mdf_t.rename(columns={0: 'kcal / g'}, inplace=True)

# pre_df = mdf_t.reset_index()  # converting multiindex to normal df
# df = pre_df.rename(columns={0: "Dane"})
# df.index.name = 'idx'
# print(df.head(20))
#
# df2 =df.groupby(['level_0', 'level_1']).sum().transpose().stack().reset_index()
#
# print(df.head(20))

# moving stuff from level_2 ('Energia', 'Białko', 'Tłuszcz' etc.)  to separate columns
# 1) creating new dfs for each
# energia = df[(df['level_2'] == "Energia")]
# energia2 = energia.rename(columns={'Dane': "Energia (kcal)"})  # new df cause inplace=True throws warning
# energia2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# bialko = df[(df['level_2'] == "Białko")]
# bialko2 = bialko.rename(columns={'Dane': "Białko (g)"})
# bialko2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# tluszcz = df[(df['level_2'] == "Tłuszcz")]
# tluszcz2 = tluszcz.rename(columns={'Dane': "Tłuszcz (g)"})
# tluszcz2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# tluszcz_nasyc = df[(df['level_2'] == "Kwasy tłuszczowe nasycone")]
# tluszcz_nasyc2 = tluszcz_nasyc.rename(columns={'Dane': "Kwasy tłuszczowe nasycone (g)"})
# tluszcz_nasyc2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# wegle = df[(df['level_2'] == "Węglowodany")]
# wegle2 = wegle.rename(columns={'Dane': "Węglowodany (g)"})
# wegle2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# cukry = df[(df['level_2'] == "Cukry proste")]
# cukry2 = cukry.rename(columns={'Dane': "Cukry proste (g)"})
# cukry2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# blonnik = df[(df['level_2'] == "Błonnik")]
# blonnik2 = blonnik.rename(columns={'Dane': "Błonnik (g)"})
# blonnik2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# sol = df[(df['level_2'] == "Sól")]
# sol2 = sol.rename(columns={'Dane': "Sól (g)"})
# sol2.drop(columns=['level_0', 'level_1', 'level_2'], inplace=True)
#
# # 2) merging all with df
# df_en = df.merge(energia2, on='idx', how='outer')
# df_en_b = df_en.merge(bialko2, on='idx', how='outer')
# df_en_b_t = df_en_b.merge(tluszcz2, on='idx', how='outer')
# df_en_b_t_tn = df_en_b_t.merge(tluszcz_nasyc2, on='idx', how='outer')
# df_en_b_t_tn_w = df_en_b_t_tn.merge(wegle2, on='idx', how='outer')
# df_en_b_t_tn_w_c = df_en_b_t_tn_w.merge(cukry2, on='idx', how='outer')
# df_en_b_t_tn_w_c_b = df_en_b_t_tn_w_c.merge(blonnik2, on='idx', how='outer')
# df_en_b_t_tn_w_c_b_s = df_en_b_t_tn_w_c.merge(sol2, on='idx', how='outer')
#
# print(df_en_b_t_tn_w_c_b_s.head(16))


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

