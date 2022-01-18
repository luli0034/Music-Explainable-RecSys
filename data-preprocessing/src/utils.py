import pandas as pd


def to_kg_format(df, h, r, t, ent2type):
    kg = pd.DataFrame(columns=['h', 'h_type', 'r', 't', 't_type'])

    kg['h'] = df[h]
    kg['h_type'] = ent2type[h]
    kg['r'] = r
    kg['t'] = df[t]
    kg['t_type'] = ent2type[t]

    if type(kg['t'][0]) == list:
        kg = kg.explode('t')


    return kg

def keys_to_kg_format(keys, h, r, t, ent2type):
    kg = pd.DataFrame(keys, columns=['h','t'])
    kg['r'] = r
    kg['h_type'] = ent2type[h]
    kg['t_type'] = ent2type[t]

    return kg[['h', 'h_type', 'r', 't', 't_type']]

def isrc_to_year(isrc):
    if type(isrc) == str:
        if int(isrc[5:7]) > 17:
            return 1900 + int(isrc[5:7])
        else:
            return 2000 + int(isrc[5:7])
    else:
        return -1

def isrc_to_country(isrc):
    if type(isrc) == str:
        return isrc[:2]
    else:
        return -1

def isrc_to_registrant(isrc):
    if type(isrc) == str:
        return isrc[2:5]
    else:
        return -1

def isrc_processing(type):
    if type=='year': 
        return isrc_to_year
    elif type=='country': 
        return isrc_to_country
    elif type=='registrant':
        return isrc_to_registrant
    else:
        raise ValueError("Wrong type")