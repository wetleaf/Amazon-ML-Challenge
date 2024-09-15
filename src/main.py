import os
import random
import pandas as pd
from pathlib import Path
import preprocessing


def train(train_data: pd.DataFrame,save_path = "../data/augmented_train_data.csv"):

    # train_data['image_link']  = pd.Series([Path(image_link).name for image_link in train_data['image_link']])
    train_data = preprocessing.remove_invalid_rows(train_data)
    augmented_train_data = preprocessing.process(train_data.iloc[:10],save_path=save_path)


    return None

def predictor(image_link, category_id, entity_name):
    '''
    Call your model/approach here
    '''
    #TODO
    return "" if random.random() > 0.5 else "10 inch"

if __name__ == "__main__":
    DATASET_FOLDER = '../data/'
    
    train_data = pd.read_csv(os.path.join(DATASET_FOLDER, 'train_data.csv'))
    model = train(train_data)

    # test = pd.read_csv(os.path.join(DATASET_FOLDER, 'test.csv'))
    
    # test['prediction'] = test.apply(
    #     lambda row: predictor(row['image_link'], row['group_id'], row['entity_name']), axis=1)
    
    # output_filename = os.path.join(DATASET_FOLDER, 'test_out.csv')
    # test[['index', 'prediction']].to_csv(output_filename, index=False)