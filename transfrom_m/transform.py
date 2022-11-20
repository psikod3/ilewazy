import numpy as np
import pandas as pd
import json

# options = {'display.max_columns': None, 'display.width': None,'display.max_rows': None, 'display.max_colwidth': 100}
# [pd.set_option(option, value) for option, value in options.items()]

# # make pycharm console view wider df
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

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

# cleaning
df.iloc[9206, 1] = np.nan  # df = df.sort_values(by=['Porcja']) one of cells was empty
df['Porcja'] = df['Porcja'].str.replace("na zdjęciu \(", '', regex=True).str.replace(' g\)', '', regex=True).str.replace('nowe ', '')
df['Białko'] = df['Białko'].str.replace(',', '.').str.replace(' g', '').str.replace('-', '0').str.replace('b.d.', '0').astype(float)
df['Błonnik'] = df['Błonnik'].str.replace(',', '.').str.replace(' g', '').str.replace('-', '0').str.replace('b.d.','0').astype(float)
df['Cukry proste'] = df['Cukry proste'].str.replace(',', '.').str.replace(' g', '').str.replace('-', '0').str.replace('b.d.', '0').astype(float)
df['Energia'] = df['Energia'].str.replace(',', '.').str.replace(' kcal', '').str.replace('-', '0').str.replace('b.d.','0').astype(int)
df['Tłuszcze nasycone'] = df['Tłuszcze nasycone'].str.replace(',', '.').str.replace(' g', '').str.replace('-','0').str.replace('b.d.', '0').astype(float)
df['Sól'] = df['Sól'].str.replace(',', '.').str.replace(' g', '').str.replace('-', '0').str.replace('b.d.', '0').astype(float)
df['Tłuszcz'] = df['Tłuszcz'].str.replace(',', '.').str.replace(' g', '').str.replace('-', '0').str.replace('b.d.','0').astype(float)
df['Węglowodany'] = df['Węglowodany'].str.replace(',', '.').str.replace(' g', '').str.replace('-', '0').str.replace('b.d.', '0').astype(float)


# checks
female = 1  # for future

# Salt check: < 0.3 g / 100 g is low, > 1.5g is high / max  6g per day
# https://www.nhs.uk/Livewell/Goodfood/Documents/having-too-much-salt-survival-guide.pdf
# https://www.nutrition.org.uk/life-stages/men/nutrition-recommendations-for-men/
def salt_check(df):
    if df['Porcja'] == '100g' and df['Sól'] == 0:
        return 'brak'
    elif df['Porcja'] == '100g' and (0.0 < df['Sól'] < 0.3):
        return 'niska'
    elif df['Porcja'] == '100g' and (0.3 <= df['Sól'] <= 1.5):
        return 'średnia'
    elif df['Porcja'] == '100g' and df['Sól'] > 1.5:
        return 'wysoka'
    elif df['Porcja'] == '100g' and pd.isna(df['Sól']):
        return 'b. d.'
    elif df['Porcja'] != '100g' and not pd.isna(df['Sól']):
        x = df['Sól'] / 6
        return str(round(x * 100)) + ' % max'
    else:
        return np.nan
df['Zaw. soli'] = df.apply(salt_check, axis=1)


# Fibre check: 3g /100g -good source, 6g - high source. 30 g per day for adults
# https://www.bda.uk.com/resource/fibre.html
# https://www.nutrition.org.uk/life-stages/men/nutrition-recommendations-for-men/
def fibre_check(df):
    if df['Porcja'] == '100g' and df['Błonnik'] == 0:
        return 'brak'
    elif df['Porcja'] == '100g' and (0 < df['Błonnik'] < 3):
        return 'przeciętne'
    elif df['Porcja'] == '100g' and (3 <= df['Błonnik'] < 6):
        return 'dobre'
    elif df['Porcja'] == '100g' and df['Błonnik'] >= 6.0:
        return 'b. dobre'
    elif df['Porcja'] == '100g' and pd.isna(df['Błonnik']):
        return 'b. d.'
    elif df['Porcja'] != '100g' and not pd.isna(df['Błonnik']):
        x = df['Błonnik'] / 30
        return str(round(x * 100)) + ' % RWS'
    else:
        return 'b. d.'
df['Źródło błonnika'] = df.apply(fibre_check, axis=1)


# Saturated fat check: sat fat-free <= 0.1g, low <= 1.5g, high > 5g / men < 31g, women < 20g per day
# Fat check: fat-free <= 0.5g, low <= 3g, high > 17.5g / women < 70 g per day, men < 97g
# https://www.nhs.uk/live-well/eat-well/food-types/different-fats-nutrition/
# https://www.nutrition.org.uk/healthy-sustainable-diets/fat/?level=Consumer
# https://www.ibdrelief.com/diet/reference-intakes-on-food-labels-explained
# https://www.nutrition.org.uk/life-stages/men/nutrition-recommendations-for-men/
def sat_fat_check(df):
    if df['Porcja'] == '100g' and df['Tłuszcze nasycone'] <= 0.1:
        return 'brak'
    elif df['Porcja'] == '100g' and (0.1 < df['Tłuszcze nasycone'] <= 1.5):
        return 'niska'
    elif df['Porcja'] == '100g' and (1.5 < df['Tłuszcze nasycone'] <= 5.0):
        return 'średnia'
    elif df['Porcja'] == '100g' and df['Tłuszcze nasycone'] > 5.0:
        return 'wysoka'
    elif df['Porcja'] == '100g' and pd.isna(df['Tłuszcze nasycone']):
        return 'b. d.'
    elif df['Porcja'] != '100g' and not pd.isna(df['Tłuszcze nasycone']) and female == 1:
        x = df['Tłuszcze nasycone'] / 20
        return str(round(x * 100)) + ' % max'
    elif df['Porcja'] != '100g' and not pd.isna(df['Tłuszcze nasycone']) and female == 0:
        x = df['Tłuszcze nasycone'] / 31
        return str(round(x * 100)) + ' % max'
    else:
        return 'b. d.'
df['Zaw. t. nasyconych'] = df.apply(sat_fat_check, axis=1)

def fat_check(df):
    if df['Porcja'] == '100g' and df['Tłuszcz'] <= 0.5:
        return 'brak'
    elif df['Porcja'] == '100g' and (0.5 < df['Tłuszcz'] <= 3.0):
        return 'niska'
    elif df['Porcja'] == '100g' and (3.0 < df['Tłuszcz'] <= 17.5):
        return 'średnia'
    elif df['Porcja'] == '100g' and df['Tłuszcz'] > 17.5:
        return 'wysoka'
    elif df['Porcja'] == '100g' and pd.isna(df['Tłuszcz']):
        return 'b. d.'
    elif df['Porcja'] != '100g' and not pd.isna(df['Tłuszcz']) and female == 1:
        x = df['Tłuszcz'] / 70
        return str(round(x * 100)) + ' % RWS'
    elif df['Porcja'] != '100g' and not pd.isna(df['Tłuszcz']) and female == 0:
        x = df['Tłuszcz'] / 97
        return str(round(x * 100)) + ' % RWS'
    else:
        return 'b. d.'
df['Zaw. tłuszczu'] = df.apply(fat_check, axis=1)


# sugar check: 5g <= is low, > 22.5g is high / 90 g per day
# carb check: / men = 333 g, women 260 per day
# https://www.nhs.uk/live-well/eat-well/food-types/how-does-sugar-in-our-diet-affect-our-health/
# https://www.ibdrelief.com/diet/reference-intakes-on-food-labels-explained
# https://www.nutrition.org.uk/life-stages/men/nutrition-recommendations-for-men/
def sugar_check(df):
    if df['Porcja'] == '100g' and df['Cukry proste'] <= 5:
        return 'niska'
    elif df['Porcja'] == '100g' and (5 < df['Cukry proste'] <= 22.5):
        return 'średnia'
    elif df['Porcja'] == '100g' and df['Cukry proste'] > 22.5:
        return 'wysoka'
    elif df['Porcja'] == '100g' and pd.isna(df['Cukry proste']):
        return 'b. d.'
    elif df['Porcja'] != '100g' and not pd.isna(df['Cukry proste']):
        x = df['Cukry proste'] / 90
        if df['Cukry proste'] > 27:
            return str(round(x * 100)) + ' % max PORCJA!'
        elif df['Cukry proste'] < 27:
            return str(round(x * 100)) + ' % max'
    else:
        return 'b. d.'
df['Zaw. cukrów prostych'] = df.apply(sugar_check, axis=1)

def carb_check(df):
    if df['Porcja'] != '100g' and not pd.isna(df['Węglowodany']) and female == 1:
        x = df['Węglowodany'] / 260
        return str(round(x * 100)) + ' % RWS'
    elif df['Porcja'] != '100g' and not pd.isna(df['Węglowodany']) and female == 0:
        x = df['Węglowodany'] / 333
        return str(round(x * 100)) + ' % RWS'
    else:
        return np.nan
df['Zaw. węglowodanów'] = df.apply(carb_check, axis=1)


# protein check: / women 45 g per day, men - 56
# https://www.nutrition.org.uk/healthy-sustainable-diets/protein/?level=Health%20professional
# https://www.ibdrelief.com/diet/reference-intakes-on-food-labels-explained
def protein_check(df):
    if df['Porcja'] != '100g' and not pd.isna(df['Białko']) and female == 1:
        x = df['Białko'] / 45
        return str(round(x * 100)) + ' % RWS'
    elif df['Porcja'] != '100g' and not pd.isna(df['Białko']) and female == 0:
        x = df['Białko'] / 56
        return str(round(x * 100)) + ' % RWS'
    else:
        return np.nan
df['Zaw. białka'] = df.apply(protein_check, axis=1)


# balance_check: carbohydrate (45%-65% of energy), protein (10%-35% of energy), and fat (20%-35% of energy)
# carbohydrate = 4.2 kcal, fats = 9.5 kcal, protein = 4.1 kcal
# https://www.brianmac.co.uk/nutrit.htm#ref
# https://pubmed.ncbi.nlm.nih.gov/16004827/
def balance_check(df):
    if df['Porcja'] != '100g' and not pd.isna(df['Porcja']) and df['Porcja'] != 0 and df['Porcja'].isnumeric():
        if float(df['Porcja']):
            protein_proportion = df['Białko'] * 4.1 / float(df['Porcja'])
            fat_proportion = df['Tłuszcz'] * 9.5 / float(df['Porcja'])
            carb_proportion = df['Węglowodany'] * 4.2 / float(df['Porcja'])
            if 0.1 <= protein_proportion <= 0.35 and 0.2 <= fat_proportion <= 0.35 and 0.45 <= carb_proportion <= 0.65:
                return "TAK"
            else:
                return np.nan
    else:
        return np.nan
df['Bilans B:T:W'] = df.apply(balance_check, axis=1)


# caloric_check: low 120 kcal / 100 g; high - 225 kcal // 2000 female, 2500 male RWS
# https://labelcalc.com/low-calorie-nutrition-label-requirements-what-food-manufacturers-need-to-know/
# https://www.wcrf-uk.org/preventing-cancer/our-cancer-prevention-recommendations/avoid-high-calorie-foods/
# https://www.nutrition.org.uk/life-stages/men/nutrition-recommendations-for-men/

def caloric__check(df):
    if df['Porcja'] == '100g' and df['Energia'] <= 120:
        return 'niska'
    elif df['Porcja'] == '100g' and (120 < df['Energia'] <= 225):
        return 'średnia'
    elif df['Porcja'] == '100g' and df['Energia'] > 225:
        return 'wysoka'
    elif df['Porcja'] == '100g' and pd.isna(df['Energia']):
        return 'b. d.'
    elif df['Porcja'] != '100g' and not pd.isna(df['Energia']) and female == 1:
        x = df['Energia'] / 2000
        return str(round(x * 100)) + ' % RWS'
    elif df['Porcja'] != '100g' and not pd.isna(df['Energia']) and female == 0:
        x = df['Energia'] / 2500
        return str(round(x * 100)) + ' % RWS'
    else:
        return 'b. d.'
df['Kaloryczność'] = df.apply(caloric__check, axis=1)

# rearranging cols
cols = df.columns.tolist()
order = [0, 4, -1, -2, 1, -3, 7, -6, 5, -7, 8, -4, 3, -5, 2, -8, 6, -9]
cols = [cols[i] for i in order]
df = df[cols]
df.columns = ['PORCJA', 'ENERGIA', 'Kaloryczność', 'Bilans B:T:W', 'BIAŁKO', 'Zaw. białka', 'TŁUSZCZ', 'Zaw. tłuszczu',
              'w tym: t. nasyc.', 'Zaw. t. nasyc.', 'WĘGLOWODANY', 'Zaw. węglow.', 'w tym: w. proste','Zaw. w. prost.',
              'BŁONNIK', 'Źródło błonnika ', 'SÓL', 'Zaw. soli']

df.reset_index(inplace=True)
df['Produkt'] = df['Produkt'].str.strip()
df = df.sort_values(by=['Produkt'])

# print(df.head(20))
# print('df', len(df.index))

df.to_pickle('ilewazy.pkl')
