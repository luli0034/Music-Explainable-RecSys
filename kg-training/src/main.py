import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
from KGE.data_utils import index_kg, convert_kg_to_index, train_test_split_no_unseen
from KGE.models.translating_based.TransE import TransE

import argparse 

def get_data(args):
    members = pd.read_csv(args.data_path+'kg_members.csv', dtype=str, delimiter=',', encoding='utf-8')
    songs = pd.read_csv(args.data_path+'kg_song.csv', dtype=str, delimiter=',', encoding='utf-8')
    user_interaction = pd.read_csv(args.data_path+'kg_user_interaction.csv', dtype=str, delimiter=',', encoding='utf-8')
    all_data = pd.concat([songs, user_interaction, members], ignore_index=True).sample(frac=1).reset_index(drop=True)
    all_data = all_data.dropna()
    all_data = all_data[['h', 'r', 't']].astype(str).to_numpy()
    # train, test = train_test_split_no_unseen(all_data, args.test_ratio, args.SEED)
    # train, valid = train_test_split_no_unseen(train, args.valid_ratio, args.SEED)
    test_size = int(args.test_ratio*len(all_data))
    valid_size = int(args.valid_ratio*len(all_data))
    np.random.shuffle(all_data)
    all_data, test = all_data[test_size:, :], all_data[:test_size, :]
    train, valid = all_data[valid_size:, :], all_data[:valid_size, :]

    return train, valid, test

def main():
    parser = argparse.ArgumentParser(description='Data processing')
    parser.add_argument("--data_path", default='./kg-data/', help="Processed KG-data")
    parser.add_argument("--test_ratio", default=0.2, help="Spliting ratio for test set")
    parser.add_argument("--valid_ratio", default=0.1, help="Spliting ratio for validation set")
    parser.add_argument("--output_path", default='./kg-training/src/output/', help="Output data path")
    parser.add_argument("--SEED", default=2021, help="Output data path")
    

    args = parser.parse_args()
    np.random.seed(args.SEED)
    train, valid, test = get_data(args)

    metadata = index_kg(train)
    
    
    train = convert_kg_to_index(train, metadata["ent2ind"], metadata["rel2ind"])
    valid = convert_kg_to_index(valid, metadata["ent2ind"], metadata["rel2ind"])
    valid = np.delete(valid, [not all(x) for x in valid != None], axis=0)
    test = convert_kg_to_index(test, metadata["ent2ind"], metadata["rel2ind"])
    test = np.delete(test, [not all(x) for x in test != None], axis=0)

    
    model = TransE(
        embedding_params={"embedding_size": 32},
        negative_ratio=4,
        corrupt_side="h+t"
    )
    model.train(train_X=train, val_X=valid, metadata=metadata, epochs=10, batch_size=512,
                early_stopping_rounds=None, restore_best_weight=False,
                optimizer=tf.optimizers.Adam(learning_rate=0.001),
                seed=12345, log_path="./tensorboard_logs", log_projector=True)

    with open(args.output_path+'ent_emb.pkl', 'wb') as f:
        pickle.dump(model.model_weights['ent_emb'], f)
    
    with open(args.output_path+'rel_emb.pkl', 'wb') as f:
        pickle.dump(model.model_weights['rel_emb'], f)

    print(123)
if __name__ == "__main__":
    main()

    