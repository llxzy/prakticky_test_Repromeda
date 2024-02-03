import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import f_oneway

FILE_PATH = './Data/transfery.csv'

df = pd.read_csv(FILE_PATH)

def process_data(dataframe, column, exclude_donated):
    if exclude_donated:
        dataframe = dataframe[dataframe['f_donor'] != 1]
    df = dataframe.dropna(subset=['clinical_gravidity', column])
    df = df[df[column].str.isnumeric()]
    df[column] = df[column].astype(int)

    all = df.clinical_gravidity.sum() / df.clinical_gravidity.count()

    bins = [0, 29, 34, 39, 100]
    
    groups = df.groupby(pd.cut(df[column], bins))

    i = 0
    split_data = {}
    group_data = {}
    for _, group in groups:
        split_data[i] = group.clinical_gravidity.sum() / group.clinical_gravidity.count()
        group_data[i] = group.clinical_gravidity
        i += 1
        
    assert(i == 4)

    table_data = {
        "všechny" : all,
        "do 29" : split_data[0],
        "30-34" : split_data[1],
        "35-39" : split_data[2],
        "40+" : split_data[3]
    }

    table = pd.DataFrame(table_data, index=[0])

    # anova
    _, pvalue = f_oneway(group_data[0], group_data[1], group_data[2], group_data[3])

    return table, pvalue
    
# A, B, C
gravidity_table, gravidity_pvalue = process_data(df, 'vek_mother', False)
embryo_table, embryo_pvalue = process_data(df, 'vek_embryo', True)

interesting_methods = ['PGT-A', 'PGT-SR', 'Karyomapping', 'OneGene']
def group_func(row):
    genetic_method = str(row['genetic_method'])
    if genetic_method == 'nan':
        return 'bez geneticke metody'
    elif genetic_method in interesting_methods:
        return genetic_method
    return 'ostatni'

# D
gm_df = df['genetic_method'].astype(str).groupby(by=lambda idx: group_func(df.loc[idx])).count().to_frame().transpose()


# E
sdf = df.dropna(subset=['clinical_gravidity', 'sex']).groupby('sex')

xx = sdf.get_group('XX').clinical_gravidity
xy = sdf.get_group('XY').clinical_gravidity

_, sex_p_value = f_oneway(xx, xy)

# F
def create_figure(table, output_file):
    x = list(table.columns)
    y = list(table.iloc[0])
    plt.xticks(rotation=45)
    plt.scatter(x, y)
    plt.savefig(output_file)


create_figure(gravidity_table, 'A.png')
create_figure(gm_df, 'D.png')


