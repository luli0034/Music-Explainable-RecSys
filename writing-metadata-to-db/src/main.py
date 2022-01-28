import numpy as np
import pandas as pd
import argparse 
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from api.database import engine, metadata, get_table_obj
from pyhocon import ConfigFactory

def parse_data(path, conf):
    df = pd.read_csv(path, encoding='utf8')
    objs = [sub_df.reset_index()[['h','r','t']].drop_duplicates() for _ , sub_df in df.groupby('r', as_index=False)]
    relations = []
    for obj in objs:
        table_info = conf[obj.iloc[0]['r']]
        obj.rename(columns={
            'h':table_info['h_col'], 
            't':table_info['t_col']
        }, inplace=True)
        relations.append(table_info['table_name'])
        obj.drop(['r'], axis=1, inplace=True)
    return objs, relations

def table_transform(objs, base, key):
    base = base.drop_duplicates().reset_index(drop=True)[['index']]
    base.rename(columns={'index':key}, inplace=True)
    for obj in objs:
        base = base.merge(obj, on=key, how='left')

    return base

def main():
    parser = argparse.ArgumentParser(description='Writing-metadata')
    parser.add_argument("--data_path", default='./kg-data/', help="Path of input data")
    parser.add_argument("--file_type", default='kg_user_interaction', help="kg_song, kg_members, or kg_user_interaction")
    parser.add_argument("--config_path", default='./table.conf', help='Path of config file')
    args = parser.parse_args()

    file_path = args.data_path + args.file_type + '.csv'
    conf = ConfigFactory.parse_file(args.config_path)
    objs, relations = parse_data(file_path, conf[args.file_type])

    conn = engine.connect()
    
    if args.file_type == 'kg_members':
        base = pd.read_csv(args.data_path + 'members.csv')
        base = base.rename(columns={'msno':'user_id'})
        data = table_transform(objs, base, 'user_id')
        data = data.to_dict(orient='records')
        columns = [Column(col, String, primary_key=True) for col in conf['table.Users.columns']]
        columns.insert(0, Column(conf['table.Users.primary_key'], String, primary_key=True))
        table = get_table_obj('Users', columns)

        try:
            table.drop(engine)
        except Exception:
            print("table not exist")

        metadata.create_all(engine)
        conn.execute(table.insert(), data)
        
    elif args.file_type == 'kg_song':
        base = pd.read_csv(args.data_path + 'songs.csv')
        df = table_transform(objs, base, 'song_id')
        data = df.to_dict(orient='records')
        columns = [Column(col, String, primary_key=True) for col in conf['table.Songs.columns']]
        columns.insert(0, Column(conf['table.Songs.primary_key'], String, primary_key=True))
        table = get_table_obj('Songs', columns)

        try:
            table.drop(engine)
        except Exception:
            print("table not exist")

        metadata.create_all(engine)
        conn.execute(table.insert(), data)

    elif args.file_type == 'kg_user_interaction':
        for idx, obj in enumerate(objs):
            table_name = relations[idx]
            cols = obj.columns.tolist()
            columns = [
                Column(cols[0], String, primary_key=True), 
                Column(cols[1], String, primary_key=True)
            ]
            table = get_table_obj(table_name, columns)

            try:
                table.drop(engine)
            except Exception:
                print("table not exist")

            metadata.create_all(engine)
            conn.execute(table.insert(), obj.to_dict(orient='records'))
    

    print(123)
if __name__ == "__main__":
    main()

    