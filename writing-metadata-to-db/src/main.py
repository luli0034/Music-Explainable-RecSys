import numpy as np
import pandas as pd
import argparse 
from sqlalchemy.orm import Session
from api.database import engine, metadata_obj, UserLikeSong


metadata_obj.create_all(engine)

conn = engine.connect()

def main():
    parser = argparse.ArgumentParser(description='Writing-metadata')
    
    args = parser.parse_args()
    
    data = [
        {'msno':'msno_4', 'song_id':'song_4'},
        {'msno':'msno_5', 'song_id':'song_5'},
        {'msno':'msno_6', 'song_id':'song_6'}
    ]
    
    conn.execute(UserLikeSong.delete())
    conn.execute(UserLikeSong.insert(), data)
    
    print(123)
if __name__ == "__main__":
    main()

    