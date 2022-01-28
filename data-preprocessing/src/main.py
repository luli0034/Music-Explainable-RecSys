import argparse 
import pandas as pd
import numpy as np
from utils import to_kg_format, isrc_processing, keys_to_kg_format
parser = argparse.ArgumentParser(description='Data processing')
parser.add_argument("--path", default='./data-preprocessing/data/source/', help="Downloaded data path")
parser.add_argument("--output_path", default='./data-preprocessing/data/', help="Output data path")

args = parser.parse_args()

ent2type = {
    'msno':'user',
    'registered_via':'registered_via',
    'membership_days':'days',
    'registration_year':'datetime',
    'bd':'days',
    'city':'category',
    'gender':'category',
    'song_id':'song',
    'song_length':'catrgory',
    'genre_ids':'category',
    'artist_name': 'artist',
    'lyricist': 'lyricist',
    'composer': 'composer',
    'song_year': 'datetime',
    'country': 'category',
    'registrant': 'person',
    'language': 'category'
}

def build_member_kg(members):
    """
    msno,city,bd,gender,registered_via,registration_init_time,expiration_date
    XQxgAYj3klVKjR3oxPPXYYFp4soD4TuBghkhMTD4oTw=,1,0,,7,20110820,20170920
    UizsfmJb9mV54qE9hCYyU07Va97c0lCRLEQX3ae+ztM=,1,0,,7,20150628,20170622

    Parameters
    ----------
    members : [type]
        [description]
    """
    members['membership_days'] = members['expiration_date'].subtract(members['registration_init_time']).dt.days.astype(int)
    members['registration_year'] = members['registration_init_time'].dt.year
    members = members.drop(['registration_init_time', 'expiration_date'], axis=1)
    members['registered_via'] = members['registered_via'].apply(lambda x: 'reg_'+str(x))
    members['city'] = members['city'].apply(lambda x: 'city_'+str(x))
    members['bd'] = members['bd'].apply(lambda x: -1 if not x else '{start}-{end}'.format(start=x//10*10, end=(x//10+1)*10))
    members['membership_days'] = members['membership_days'].apply(lambda x: -1 if not x else '{start}-{end}'.format(start=x//365*365, end=(x//365+1)*365))

    members = members.fillna(-1)
    member_kg = pd.DataFrame(columns=['h','h_type','r','t','t_type'])
    member_kg = pd.concat([member_kg, to_kg_format(df=members, h='msno', r='registered_via', t='registered_via', ent2type=ent2type)])
    member_kg = pd.concat([member_kg, to_kg_format(df=members, h='msno', r='membership_days', t='membership_days', ent2type=ent2type)])
    member_kg = pd.concat([member_kg, to_kg_format(df=members, h='msno', r='age', t='bd', ent2type=ent2type)])
    member_kg = pd.concat([member_kg, to_kg_format(df=members, h='msno', r='live_in', t='city', ent2type=ent2type)])
    member_kg = pd.concat([member_kg, to_kg_format(df=members, h='msno', r='gender', t='gender', ent2type=ent2type)])
    member_kg = member_kg[member_kg['t']!=-1]
    member_kg = member_kg.applymap(str.strip)
    return member_kg


def build_song_kg(songs, songs_extra):
    """
    song_id,song_length,genre_ids,artist_name,composer,lyricist,language
    CXoTN1eb7AI+DntdU1vbcwGRV4SCIDxZu+YD8JP8r4E=,247640,465,張信哲 (Jeff Chang),董貞,何啟弘,3.0
    o0kFgae9QtnYgRkVPqLJwa05zIhRlUjfF7O1tDw0ZDU=,197328,444,BLACKPINK,TEDDY|  FUTURE BOUNCE|  Bekuh BOOM,TEDDY,31.0
    DwVvVurfpuz+XPuFvucclVQEyPqcpUkHR0ne1RQzPs0=,231781,465,SUPER JUNIOR,,,31.0

    song_id,name,isrc
    LP7pLJoJFBvyuUwvu+oLzjT+bI+UeBPURCecJsX1jjs=,我們,TWUM71200043
    ClazTFnk6r0Bnuie44bocdNMM3rdlrq0bCGAsGUWcHE=,Let Me Love You,QMZSY1600015
    u2ja/bZE3zhCGxvbbOB3zOoUjx27u40cf5g09UXMoKQ=,原諒我,TWA530887303

    Parameters
    ----------
    songs : [type]
        [description]
    songs_extra : [type]
        [description]
    """
    def split(x):
        try:
            x = x.split('|')
        except:
            x = -1
        return x

    _mean_song_length = np.mean(songs['song_length'])
    songs['song_length'] = songs['song_length'].apply(lambda x: 'long' if x>_mean_song_length else 'short')
    songs['genre_ids'].fillna(-1, inplace=True)
    songs['genre_ids'] = songs['genre_ids'].apply(lambda x: split(x))
    songs['composer'].fillna(-1, inplace=True)
    songs['composer'] = songs['composer'].apply(lambda x: split(x))
    songs['lyricist'].fillna(-1, inplace=True)
    songs['lyricist'] = songs['lyricist'].apply(lambda x: split(x))
    songs['language'] = songs['language'].apply(lambda x: 'lng_'+str(x))

    songs = songs.fillna(-1)
    song_kg = pd.DataFrame(columns=['h','h_type','r','t','t_type'])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='len_belongs', t='song_length', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='genre_belongs', t='genre_ids', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='sing_by', t='artist_name', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='composer_is', t='composer', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='lyricist_is', t='lyricist', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='language_in', t='language', ent2type=ent2type)])

    songs_extra['song_year'] = songs_extra['isrc'].apply(isrc_processing('year'))
    songs_extra['song_year'] = songs_extra['song_year'].apply(lambda x: -1 if not x else '{start}-{end}'.format(start=x//5*5, end=(x//5+1)*5))
    songs_extra['country'] = songs_extra['isrc'].apply(isrc_processing('country'))
    songs_extra['registrant'] = songs_extra['isrc'].apply(isrc_processing('registrant'))
    songs_extra.drop(['isrc', 'name'], axis = 1, inplace = True)
    songs = songs.merge(songs_extra, on='song_id', how='left')
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='song_year', t='song_year', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='song_country', t='country', ent2type=ent2type)])
    song_kg = pd.concat([song_kg, to_kg_format(df=songs, h='song_id', r='registrant_by', t='registrant', ent2type=ent2type)])
    song_kg = song_kg[song_kg['t']!=-1]

    return song_kg, songs
                                              
def build_user_interaction(train, songs):
    """
    msno,song_id,source_system_tab,source_screen_name,source_type,target
    FGtllVqz18RPiwJj/edr2gV78zirAiY/9SmYvia+kCg=,BBzumQNXUHKdEBOB7mAJuzok+IJA1c2Ryg/yzTF6tik=,explore,Explore,online-playlist,1
    Xumu+NIjS6QYVxDS4/t3SawvJ7viT9hPKXmf0RtLNx8=,bhp/MpSNoqoxOIB+/l8WPqu6jldth4DIpCm3ayXnJqM=,my library,Local playlist more,local-playlist,1

    Parameters
    ----------
    train : [type]
        [description]
    songs : [type]
        [description]
    """
    train.drop(['source_system_tab', 'source_screen_name', 'source_type'], axis = 1, inplace = True)
    user_interaction = pd.DataFrame(columns=['h','h_type','r','t','t_type'])
    user_interaction = pd.concat([user_interaction, to_kg_format(df=train, h='msno', r='has_interest', t='song_id', ent2type=ent2type)])

    train = train.merge(songs, on='song_id', how='left')
    # gerne
    user_gerne = train[['msno', 'genre_ids']].explode('genre_ids')
    user_genre_top_3 = dict(user_gerne.groupby('msno', observed=True)['genre_ids'].value_counts().groupby(level=0).head(3)).keys()
    user_interaction = pd.concat([user_interaction, keys_to_kg_format(keys=user_genre_top_3, h='msno', r='like_genre', t='genre_ids', ent2type=ent2type)])
    # artist
    user_artist_top_3 = dict(train.groupby('msno', observed=True)['artist_name'].value_counts().groupby(level=0).head(3)).keys()
    user_interaction = pd.concat([user_interaction, keys_to_kg_format(keys=user_artist_top_3, h='msno', r='like_artist', t='artist_name', ent2type=ent2type)])
    # composer
    user_composer = train[['msno', 'composer']].explode('composer')
    user_composer_top_3 = dict(user_composer.groupby('msno', observed=True)['composer'].value_counts().groupby(level=0).head(3)).keys()
    user_interaction = pd.concat([user_interaction, keys_to_kg_format(keys=user_composer_top_3, h='msno', r='like_composer', t='composer', ent2type=ent2type)])
    # lyricist
    user_lyricist = train[['msno', 'lyricist']].explode('lyricist')
    user_lyricist_top_3 = dict(user_lyricist.groupby('msno', observed=True)['lyricist'].value_counts().groupby(level=0).head(3)).keys()
    user_interaction = pd.concat([user_interaction, keys_to_kg_format(keys=user_lyricist_top_3, h='msno', r='like_lyricist', t='lyricist', ent2type=ent2type)])
    
    user_interaction = user_interaction[user_interaction['t']!=-1]
    return user_interaction
    

def main():

    members = pd.read_csv(args.path + 'members.csv', parse_dates=['registration_init_time','expiration_date'])
    members = members.sample(frac=0.5, random_state=2021).reset_index(drop=True)
    member_ids = members[['msno']]
    msno2index = {v: f'user_{k}' for k, v in member_ids.to_dict('dict')['msno'].items()}
    member_ids['index'] = member_ids['msno'].apply(lambda msno: msno2index[msno])
    members['msno'] = members['msno'].apply(lambda msno: msno2index[msno])
    member_kg = build_member_kg(members)    

    songs = pd.read_csv(args.path + 'songs.csv',dtype={'genre_ids': str,
                                                  'language' : str,
                                                  'artist_name' : str,
                                                  'composer' : str,
                                                  'lyricist' : str,
                                                  'song_id' : str})
    songs = songs.sample(frac=0.1, random_state=2021).reset_index(drop=True)                                                  
    song_ids = songs[['song_id']]                                                  
    song2index = {v: f'song_{k}' for k, v in song_ids.to_dict('dict')['song_id'].items()}
    song_ids['index'] = song_ids['song_id'].apply(lambda song_id: song2index[song_id])
    songs['song_id'] = songs['song_id'].apply(lambda song_id: song2index[song_id])
    songs_extra = pd.read_csv(args.path + 'song_extra_info.csv')    
    songs_extra = songs_extra[songs_extra['song_id'].isin(song2index)].reset_index(drop=True)
    songs_extra['song_id'] = songs_extra['song_id'].apply(lambda song_id: song2index[song_id])
    song_kg, songs = build_song_kg(songs, songs_extra)
    
    train = pd.read_csv(args.path + 'train.csv', dtype={'msno' : str,
                                                'source_system_tab' : str,
                                                  'source_screen_name' : str,
                                                  'source_type' : str,
                                                  'target' : np.uint8,
                                                  'song_id' : str})
    train = train[train['target']==1].reset_index(drop=True)
    train = train[train['msno'].isin(msno2index)].reset_index(drop=True)
    train['msno'] = train['msno'].apply(lambda msno: msno2index[msno])
    train = train[train['song_id'].isin(song2index)].reset_index(drop=True)
    train['song_id'] = train['song_id'].apply(lambda song_id: song2index[song_id])    
    user_interaction = build_user_interaction(train, songs)

    member_kg.to_csv(args.output_path+'kg_members.csv', index=False, encoding='utf8')
    member_ids.to_csv(args.output_path + 'members.csv', index=False, encoding='utf8')
    song_kg.to_csv(args.output_path+'kg_song.csv', index=False, encoding='utf8')
    song_ids.to_csv(args.output_path + 'songs.csv', index=False, encoding='utf8')
    user_interaction.to_csv(args.output_path+'kg_user_interaction.csv', index=False, encoding='utf8')

if __name__ == "__main__":
    main()