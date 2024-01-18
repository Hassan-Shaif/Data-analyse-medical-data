# import libraries

import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# lees orderlines file en rename het dataframe_1
orderlines4 = pd.read_csv('orderlines4.csv', delimiter=';', low_memory=False)

# code om alle kolommen te kunnen zien
pd.set_option('display.max_columns', None)
#  De hoofdletters van medicijnnamen vervangen door kleine letters
orderlines4['product_name'] = orderlines4['product_name'].str.lower()

# medicijnnamen corrigeren
orderlines4['product_name'] = orderlines4['product_name'].str.replace('parazedamol', 'paracetamol')
orderlines4['product_name'] = orderlines4['product_name'].str.replace('dexamethazon', 'dexamethason')

# De prijs van medicijn Priadel waar het 4.76 is, vervangen door 4.67
orderlines4.loc[
    (orderlines4['product_name'] == 'priadel') & (orderlines4['verkoopprijs'] == 4.76), 'verkoopprijs'] = 4.67
# code to check if it is already changed
# print(dataframe_1.loc[dataframe_1['product_name'] == 'priadel'])

# lees product_info file en rename het dataframe_2
product_info_new = pd.read_csv('product_info_new.csv')

#  De hoofdletters van medicijnnamen in product info file vervangen door kleine letters
product_info_new['product_name'] = product_info_new['product_name'].str.lower()
## medicijnnamen corrigeren in product info file
product_info_new['product_name'] = product_info_new['product_name'].str.replace('parazedamol', 'paracetamol')
product_info_new['product_name'] = product_info_new['product_name'].str.replace('dexamethazon', 'dexamethason')

# maak een nieuw csv file met alle kolommen van orderline file en kostprijs kolom van product info file
# Ik heb een nieuw csv file gemaakt, omdat ik niet iets wil veranderen in orderline en product info files
merged_df = pd.merge(orderlines4, product_info_new[['product_name', 'kostprijs']], on='product_name', how='left')

# save the new csv file as merged_df en less het
merged_df.to_csv('merged_file.csv', index=False)
merged_files_productinfo_orderlines = pd.read_csv('merged_file.csv')
# adjust tijd formaat
merged_files_productinfo_orderlines['date'] = pd.to_datetime(merged_files_productinfo_orderlines['date'], format='%d/%m/%Y')
merged_files_productinfo_orderlines['year'] = merged_files_productinfo_orderlines['date'].dt.year
merged_files_productinfo_orderlines['month'] = merged_files_productinfo_orderlines['date'].dt.month

# kostprijs per product
merged_files_productinfo_orderlines['kostprij'] = merged_files_productinfo_orderlines['kostprijs']
# Berken de totale kostprijs > kostprijs per product * de aantal verkochte producten
merged_files_productinfo_orderlines['kostprijs'] = merged_files_productinfo_orderlines['kostprijs'] * merged_files_productinfo_orderlines['amount']

# bereken de omzet per product
merged_files_productinfo_orderlines['omzet'] = merged_files_productinfo_orderlines['verkoopprijs'] * merged_files_productinfo_orderlines['amount']

# berekn de brutowinst
merged_files_productinfo_orderlines['brutowinst'] = merged_files_productinfo_orderlines['omzet'] - merged_files_productinfo_orderlines['kostprijs']

# omzet en brutowinst per product

# maak twee dic, de key is de product_name en de omzet is de value voor de eerste en de brutowinst voor de tweede.Om grafiek te maken
total_omzet_per_product = dict(merged_files_productinfo_orderlines.groupby('product_name')['omzet'].sum())
total_brutowinst_per_product = dict(merged_files_productinfo_orderlines.groupby('product_name')['brutowinst'].sum())

# Vraag 8: Kijk naar alle influenza en corona vaccinaties en bepaal of je een patroon/verband ziet.
# Probeer dit te verklaren.

# graphiek voor (influenze vacc 2021 en corona vacc 2021)

# Filter data voor ('influenze vacc 2021' and 'corona vacc 2021)
infuenze_corona_2021 = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'].isin(['influenza vacc. 2021', 'corona vacc. 2021']) & (
        merged_files_productinfo_orderlines['date'].dt.year == 2021)]
# groep by product_name, year, and month  om de total verkoop per maand te hebben

monthly_amount_vergelijking = infuenze_corona_2021.groupby(['product_name', 'year', 'month'])[
    'amount'].sum().reset_index()

# Plotting de vergelijking
plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
for product in monthly_amount_vergelijking['product_name'].unique():
    product_data = monthly_amount_vergelijking[monthly_amount_vergelijking['product_name'] == product]
    plt.plot(product_data['month'], product_data['amount'], marker='o', linestyle='-', label=product)

plt.xlabel('Maand')
plt.ylabel('Aantal Vaccinaties verkoop')
plt.title('Vergelijking van de verkoop van corona en influenzavaccinatie in 2021')
plt.xticks(range(1, 13), ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov',
                          'dec'])  # Setting ticks for each month

plt.legend()
plt.grid(True)
plt.savefig('Vergelijking van de verkoop van corona en influenzavaccinatie in 2021.png')
plt.show()

# grafiek voor alle jaren
# Filter data for the specified products and years
infuenze_corona = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'].isin([
    'influenza vacc. 2018',
    'influenza vacc. 2020',
    'influenza vacc. 2019',
    'influenza vacc. 2022',
    'corona vacc. 2022',
    'influenza vacc. 2021',
    'corona vacc. 2021',
])]

# Group by product_name, year, and quarter (3-month intervals) to get total sales per quarter
quarterly_sales = infuenze_corona.groupby([
    'product_name',
    infuenze_corona['date'].dt.to_period('Q')
])['amount'].sum().reset_index()

# Plotting the comparison
plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
for product in quarterly_sales['product_name'].unique():
    product_data = quarterly_sales[quarterly_sales['product_name'] == product]
    plt.plot(product_data['date'].astype(str), product_data['amount'], marker='o', linestyle='-', label=product)

# Extract unique months and years from the data
unique_dates = quarterly_sales['date'].dt.to_timestamp().dt.to_period('M').astype(str).unique()

# Generate ticks with the desired format m-yyyy te seprate months and years
ticks = [date.split('-')[0] + '-' + date.split('-')[1] for date in unique_dates]

# Set ticks on the x-axis
plt.xticks(range(len(unique_dates)), ticks, rotation='vertical')
plt.xlabel('Date (Month-Year)')
plt.ylabel('Number of Vaccines Sold')
plt.title('Comparison of Corona and Influenza Vaccination Sales (Quarterly)')
plt.legend()
plt.grid(True)
# plt.savefig('Comparison of Corona and Influenza Vaccination Sales (Quarterly).png')
plt.show()

# Vraag 9A: Test: Bewijzen van een vermoeden: Colecalciferol is een vitamine D preparaat en Solaris Sunprotect een zonnebrandcreme.
# Welk verkooppatroon denk je dat zich voor deze middelen in de loop van een jaar (bijvoorbeeld 2018) aftekent?
# Beschrijf dit patroon en breng dit met behulp van een grafiek in kaart. Bepaald vooraf welk grafiektype hiervoor geschikt zou zijn.


# grafiek voor alle jaren
# filter Colecalciferol data from df3
vitamine_D = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'colecalciferol']
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'amount'
vitamine_D.set_index('date', inplace=True)
quarterly_vitamine_D_amount = vitamine_D['amount'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag) om duidelijker grafiek te hebben
formatted_vitamine_D_index = quarterly_vitamine_D_amount.index.strftime('%Y-%m')

# doe hetzelfde met sunprotect om vergelijking tussen die twee te maken
sunprotect = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'solaris sunprotect']
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'amount'
sunprotect.set_index('date', inplace=True)
quarterly_sunprotect_amount = sunprotect['amount'].resample('4M').sum()
formatted_sunprotect_index = quarterly_sunprotect_amount.index.strftime('%Y-%m')

# plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_vitamine_D_index, quarterly_vitamine_D_amount.values, label='Vitamin D', color='skyblue')
plt.plot(formatted_sunprotect_index, quarterly_sunprotect_amount.values, label='Sun-protect', color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount of Sales')
plt.title('Comparison of Vitamin D and Sun-protect Sales', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
# plt.savefig('Comparison of Vitamin D and Sun-protect Sales.png')
plt.show()

# grafiek voor 2018

# Filter Colecalciferol data for the year 2018 from df3
vitamine_D_2018 = vitamine_D.query('date.dt.year == 2018')

# Filter Sun-protect data for the year 2018 from df3
sunprotect_2018 = sunprotect.query('date.dt.year == 2018')

quarterly_vitamine_D_2018_amount = vitamine_D_2018['amount'].resample('M').sum()
formatted_vitamine_D_2018_index = quarterly_vitamine_D_2018_amount.index.strftime('%Y-%m')

# Resample the data for Sun-protect to four-month intervals ('4M') and sum the 'amount'
quarterly_sunprotect_2018_amount = sunprotect_2018['amount'].resample('4M').sum()
formatted_sunprotect_2018_index = quarterly_sunprotect_2018_amount.index.strftime('%Y-%m')

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_vitamine_D_2018_index, quarterly_vitamine_D_2018_amount.values, label='Vitamin D', color='skyblue')
plt.plot(formatted_sunprotect_2018_index, quarterly_sunprotect_2018_amount.values, label='Sun-protect', color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount of Sales')
plt.title('Comparison of Vitamin D and Sun-protect Sales in 2018', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Comparison of Vitamin D and Sun-protect Sales 2018.png')
plt.show()

# Vraag 9B: Test: Bewijzen van een vermoeden, zoek correlatiecoefficient op.
# Zoek op voor welke kwaal de middelen
# Desloratidine en Hydrocortison worden voorgeschreven.
# Welke correlatie vermoed je? Bewijs jouw vermoeden met een
# grafiek. Is de correlatiecoefficient positief of negatief?

# we gaan twee grafieken maken voor deze vraag. De ene voor een speciefic jaar ex(2021)
# en de andere voor alle jaren

# eerste grafiek voor 2021


# Filter solaris desloratidine, hydrocortison  van dataframe3
selected_products = ['desloratidine', 'hydrocortison']
Desloratidine_Hydrocortison = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'].isin(selected_products)]

# voeg date kolomn in de nieuwe dataframe toe
Desloratidine_Hydrocortison.loc[:, 'date'] = pd.to_datetime(Desloratidine_Hydrocortison['date'])

# Filter speciefic jaren(2021)


years_filtered = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['date'].dt.year.isin([2021])].copy()
years_filtered['period'] = years_filtered['date'].dt.to_period('M').astype(str)

# Groep by product_name and period (month)
monthly_aantal_vergelijking = (
    Desloratidine_Hydrocortison.groupby(['product_name', years_filtered['period']])
    ['amount'].sum().reset_index()
)
# Plotting de vergelijking
plt.figure(figsize=(10, 6))
for product in monthly_aantal_vergelijking['product_name'].unique():
    product_data = monthly_aantal_vergelijking[monthly_aantal_vergelijking['product_name'] == product]
    # zonder de volgende if statemnet werk het niet, het is ook niet zo duidelijk voor mij waarrom.
    if product == 'desloratidine':
        plt.plot(product_data['period'], product_data['amount'], marker='o', linestyle='-', label='desloratidine')
    elif product == 'hydrocortison':
        plt.plot(product_data['period'], product_data['amount'], marker='*', linestyle='-', label='hydrocortison')

plt.xticks(rotation='vertical')
plt.xlabel('Month')
plt.ylabel('Amount of Sales')
plt.title('Comparison of Desloratidine and Hydrocortisont Sales in 2021')
plt.yticks(range(500, 18000, 1000))
plt.xticks(range(0, 12), ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov',
                          'dec'])  # Setting ticks for each month
plt.legend()
plt.grid(True)
plt.savefig('Comparison of Desloratidine and Hydrocortisont Sales in 2021')
plt.show()

# Grafiek voor alle jaren


# - som aantal/ amount, van elkaar verglijken.
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de de amount
# filter desloratidine data from df3
desloratidine = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'desloratidine']

# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'amount'
desloratidine.set_index('date', inplace=True)
quarterly_desloratidine_amount = desloratidine['amount'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag) om duidelijker grafiek te hebben
formatted_desloratidine_index = quarterly_desloratidine_amount.index.strftime('%Y-%m')

# doe hetzelfde met vaporub om vergelijking tussen die twee te maken
hydrocortison = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'hydrocortison']
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'amount'
hydrocortison.set_index('date', inplace=True)
quarterly_hydrocortison_amount = hydrocortison['amount'].resample('4M').sum()
formatted_hydrocortison_index = quarterly_hydrocortison_amount.index.strftime('%Y-%m')

# plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_desloratidine_index, quarterly_desloratidine_amount.values, label='desloratidine_amount_sales')
plt.plot(formatted_hydrocortison_index, quarterly_hydrocortison_amount.values, label='hydrocortison_amount_sales')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount')
plt.title('Comparison of Desloratidine and Hydrocortisont Sales ', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Comparison of Desloratidine and Hydrocortisont Sales.png')
plt.show()

# Vraag 10: Verklaar een patroon en zoek bewijs voor causaliteit.
# Breng de jaaromzet van de jaren 2016 – 2022 van het middel dexamethazon in kaart
# en probeer het patroon te verklaren wat je daar ziet.
# Welke causaliteit denk je te zien? Welk bewijs kun je daarvoor vinden?


dexamethason = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'dexamethason']

# Groep by product_name and year, and sum the omzet per year
monthly_aantal_vergelijking = (
    dexamethason.groupby(['year'])
    ['omzet'].sum().reset_index())

# Plotting the bar chart and adding some styles
plt.bar(monthly_aantal_vergelijking['year'], monthly_aantal_vergelijking['omzet'], label='omzet', color='skyblue',
        edgecolor='black',
        linewidth=1.5,
        alpha=0.8,
        hatch='//')

plt.ylabel('Omzet in Euro')
plt.xlabel('Year')
plt.title("Dexamethason Omzet ")

plt.yticks([100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000],
           ['100K', '200K', '300K', '400K', '500K', '600K', '700K', '800K', '900K', '1M'])
plt.xticks([2020, 2021, 2022])
plt.legend()

plt.savefig("Dexamethason Omzet.png")
plt.show()

# Vraag 11A: Wat is er aan de hand als je kijkt naar Paracetamol en Ibuprofen
# kostprijs en omzet bij parcetmol hebben geen relatie, maar andere medicijnen wel,

paracetamol = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'paracetamol']

# grafiek maken voor de kostprijs en verkoopprijs van paracetmol

# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'kostprijs'
paracetamol.set_index('date', inplace=True)
quarterly_kostprij = paracetamol['kostprij'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_kostprijs_index = quarterly_kostprij.index.strftime('%Y-%m')

quarterly_verkooprijs = paracetamol['verkoopprijs'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_verkoopprijs_index = quarterly_verkooprijs.index.strftime('%Y-%m')

# Plotting the comparison
plt.figure(figsize=(10, 6))
plt.plot(formatted_kostprijs_index, quarterly_kostprij.values, label='Paracetamol Kostprijs', marker='*',
         color='skyblue')
plt.plot(formatted_verkoopprijs_index, quarterly_verkooprijs.values, label='Paracetamol Verkoopprijs', marker='*',
         color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Prijs in euro')
plt.title("Paracetoml Kostprijs en Verkoopprijs vergelijking", color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Paracetoml Kostprijs en Verkoopprijs vergelijking.png')
plt.show()

# grafiek maken voor de kostprijs en verkoopprijs van ibuprofen
ibuprofen = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'ibuprofen']

# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'kostprijs'
ibuprofen.set_index('date', inplace=True)
quarterly_kostprij = ibuprofen['kostprij'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_kostprijs_index = quarterly_kostprij.index.strftime('%Y-%m')

quarterly_verkooprijs = ibuprofen['verkoopprijs'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_verkoopprijs_index = quarterly_verkooprijs.index.strftime('%Y-%m')

# Plotting the comparison
plt.figure(figsize=(10, 6))
plt.plot(formatted_kostprijs_index, quarterly_kostprij.values, label='Ibuprofen Kostprijs', marker='*', color='skyblue')
plt.plot(formatted_verkoopprijs_index, quarterly_verkooprijs.values, label='Ibuprofen Verkoopprijs', marker='*',
         color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Prijs in euro')
plt.title("Ibuprofen Kostprijs en Verkoopprijs vergelijking", color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Ibuprofen Kostprijs en Verkoopprijs vergelijking.png')
plt.show()

# Vraag 11B: Kijk naar de medicijnen Camcolit en priadel en onderzoek en leg uit wat daar aan de hand is.

# We gaan twee grfieken maken voor camcolit en priadel
# de ene om hun aantal verkoops te vergelijken
# en de andere om te vergelijken tuseen de total omzet van beide

# grafiek 1
# - verkoopprijs van beiden verglijken in een grafiek,
# filter de df3 om camcolit data te hebben
camcolit = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'camcolit']
camcolit.set_index('date', inplace=True)
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'omzet'
quarterly_camcolit_verkoopprijs = camcolit['verkoopprijs'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag) om duidelijker grafiek te hebben
formatted_camcolit_index = quarterly_camcolit_verkoopprijs.index.strftime('%Y-%m')

# doe hetzelfde met priadel om vergelijking tussen die twee te maken
priadel = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'priadel']

priadel.set_index('date', inplace=True)
quarterly_priadel_amount = priadel['verkoopprijs'].resample('4M').sum()
formatted_priadel_index = quarterly_priadel_amount.index.strftime('%Y-%m')

# plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_camcolit_index, quarterly_camcolit_verkoopprijs.values, label='camcolit verkoopprijs', marker='*',
         color='skyblue')
plt.plot(formatted_priadel_index, quarterly_priadel_amount.values, label='priadel verkoopprijs', marker='*',
         color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Verkoopprijs')
plt.title('Camcolit en Priadel Verkoopprijs Vergelijking', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Camcolit en Priadel Verkoopprijs Vergelijking.png')
plt.show()

# Grafiek 2
# - aantal verkoops van beiden vergelijken in een grafiek,

# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'omzet'
quarterly_camcolit_amount = camcolit['amount'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag) om duidelijker grafiek te hebben
formatted_camcolit_index = quarterly_camcolit_amount.index.strftime('%Y-%m')

# doe hetzelfde met priadel om vergelijking tussen die twee te maken
quarterly_priadel_amount = priadel['verkoopprijs'].resample('4M').sum()
formatted_priadel_index = quarterly_priadel_amount.index.strftime('%Y-%m')

# plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_camcolit_index, quarterly_camcolit_amount.values, label='Aantal verkopen van Camcolit', marker='*',
         color='skyblue')
plt.plot(formatted_priadel_index, quarterly_priadel_amount.values, label='Aantal verkopen van Priadel', marker='*',
         color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Aantal verkopen')
plt.title('Aantal verkopen van Camcolit en Priadel Vergelijking', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Aantal verkopen van Camcolit en Priadel Vergelijking.png')
plt.show()

# Vraag 12: Wat valt je op aan de volgende medicijnen:


# - oscillococcinum

oscillococcinum = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'oscillococcinum']
# grafiek  1 voor amount
# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'amount'
oscillococcinum.set_index('date', inplace=True)
quarterly_amount = oscillococcinum['amount'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_amount_index = quarterly_amount.index.strftime('%Y-%m')

# Plotting the comparison
plt.figure(figsize=(10, 6))
plt.plot(formatted_amount_index, quarterly_amount.values, label='Oscillococcinum Amount of Sales', marker='*',
         color='skyblue')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount')
plt.title('Oscillococcinum Sales ', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Oscillococcinum Sales.png')
plt.show()

# grafie voor de omzet van oscillococcinum
# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'amount'
quarterly_omzet = oscillococcinum['omzet'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_omzet_index = quarterly_omzet.index.strftime('%Y-%m')

# Plotting the comparison
plt.figure(figsize=(10, 6))
plt.plot(formatted_omzet_index, quarterly_omzet.values, label='Oscillococcinum Omzet', marker='*', color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Omzet')
plt.title('Oscillococcinum  Omzet ', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Oscillococcinum Omzet.png')
plt.show()

# - Hoestdrank en vaporub

# grafiek 1
# - omzet van beiden verglijken in een grafiek,
# filter de df3 om hoestdrank data te hebben
hoestdrank = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'hoestdrank']
hoestdrank.set_index('date', inplace=True)
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de 'omzet'
quarterly_hoestdrank_omzet = hoestdrank['omzet'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag) om duidelijker grafiek te hebben
formatted_hoestdrank_index = quarterly_hoestdrank_omzet.index.strftime('%Y-%m')

# doe hetzelfde met vaporub om vergelijking tussen die twee te maken
vaporub = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'vaporub']
vaporub.set_index('date', inplace=True)
quarterly_vaporub_omzet = vaporub['omzet'].resample('4M').sum()
formatted_vaporub_index = quarterly_vaporub_omzet.index.strftime('%Y-%m')

# plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_hoestdrank_index, quarterly_hoestdrank_omzet.values, label='hoestdrank omzet', marker='*',
         color='skyblue')
plt.plot(formatted_vaporub_index, quarterly_vaporub_omzet.values, label='vaporup omzet', marker='*', color='red')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Omzet in euro')
plt.title('Hoestdrank en Vaporub Omzet', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Hoestdrank en Vaporub Omzet.png')
plt.show()

# grafiek 2
# - som aantal/ amount, van elkaar verglijken.
# Resample de data naar vier-maandelijkse intervallen ('4M') en sum de de amount
quarterly_hoestdrank_amount = hoestdrank['amount'].resample('4M').sum()
# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag) om duidelijker grafiek te hebben
formatted_hoestdrank_index = quarterly_hoestdrank_amount.index.strftime('%Y-%m')

# doe hetzelfde met vaporub om vergelijking tussen die twee te maken
quarterly_vaporub_amount = vaporub['amount'].resample('4M').sum()
formatted_vaporub_index = quarterly_vaporub_amount.index.strftime('%Y-%m')

# plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_hoestdrank_index, quarterly_hoestdrank_amount.values, label='vaporup_amount_sales')
plt.plot(formatted_vaporub_index, quarterly_vaporub_amount.values, label='hoestdrank_amount_sales')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount')
plt.title('Hoestdrank en Vaporub Sales', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Hoestdrank en Vaporub Sales.png')
plt.show()

# -citalopram

# - amount/aantal overtijd
# fileter citalopram  and sum the amount monthly
citalopram = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'citalopram']

# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'amount'
citalopram.set_index('date', inplace=True)
quarterly_amount = citalopram['amount'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_index = quarterly_amount.index.strftime('%Y-%m')

plt.figure(figsize=(10, 6))
plt.plot(formatted_index, quarterly_amount.values, marker='*', label='Amount of Sales')
plt.xticks(rotation=45, fontsize=10)
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount of Sales')
plt.title('Citalopram Sales')
plt.grid(True)
plt.legend()
plt.savefig('Citalopram Sales.png')
plt.show()

# resamplet de data naar vier-maandelijkse intervallen ('Q')
# en aggregeert de omzet om duidelijker grafiek te hebben

quarterly_omzet = citalopram['omzet'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_index = quarterly_omzet.index.strftime('%Y-%m')
# Plotting
plt.figure(figsize=(10, 6))
plt.plot(formatted_index, quarterly_omzet.values, marker='o', label='Omzet of Sales')
plt.xlabel('Citalopram  Omzet')
plt.ylabel('Omzet')
plt.title('Citalopram Omzet ')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('citalopram Omzet Over Tijd.png')
plt.show()

# foliumzuur

# - amount/ aantal over tijd
# filter foliumzuur from dataframe3 and sum the amount
foliumzuur = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'foliumzuur']

# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'omzet'
foliumzuur.set_index('date', inplace=True)
quarterly_amount = foliumzuur['amount'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_index = quarterly_amount.index.strftime('%Y-%m')

plt.figure(figsize=(10, 6))
plt.plot(formatted_index, quarterly_amount.values, label='amount', marker='*')
plt.xticks(rotation=45, fontsize=10)
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Amount of Sales')
plt.title('Foliumzuur Sales', color='darkblue')
plt.grid(True)
plt.legend()
plt.savefig('Foliumzuur Sales.png')
plt.show()

# graf2
# - omzet over tijd
# filter foliumzuur from dataframe3 and sum the omzet
foliumzuur = merged_files_productinfo_orderlines[merged_files_productinfo_orderlines['product_name'] == 'foliumzuur']

# Resample de data naar vier-maandelijkse intervallen ('4M') en aggregeer de 'omzet'
foliumzuur.set_index('date', inplace=True)
quarterly_omzet = foliumzuur['omzet'].resample('4M').sum()

# Formatteren van de datetime-index naar alleen maand en jaar (zonder dag)
formatted_index = quarterly_omzet.index.strftime('%Y-%m')

plt.figure(figsize=(10, 6))
plt.plot(formatted_index, quarterly_omzet.values, label='omzet', marker='*')
plt.xlabel('Time (Four-Month Intervals)')
plt.ylabel('Omzet')
plt.title('Foliumzuur Omzet', color='darkblue')
plt.xticks(rotation=45, fontsize=10)
plt.grid(True)
plt.legend()
plt.savefig('Foliumzuur Omzet.png')
plt.show()
