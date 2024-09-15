from paddleocr import PaddleOCR
import os
import pandas as pd
import filter
from tqdm import tqdm
import logging
import re
import constants

logging.disable(level=logging.INFO)

def clean_values(vu):
    # val,unit = val.split(' ',1)
    if ']' in vu:
        val, unit = vu.split(']',1)
        unit = unit.strip()
        num = '([0-9]*[.]?[0-9]+)'
        matches = re.findall(num, val)
        if len(matches) > 1:
            return matches[-1]+' '+val
    return vu

def remove_invalid_rows(train_data):
    # train_data = train_data.loc[train_data['entity_value'].split(' ', 1)[1] in constants.allowed_units]
    train_data.loc[ 'entity_value' ] = train_data.apply(lambda row: clean_values(row['entity_value']), axis=1)
    return train_data

def extract_texts_with_coordinates(ocr,img_path):

    result = []
    extracted_text = ocr.ocr(img_path, cls=True)[0] 
    # print(extracted_text)
    if extracted_text:
        result = [[element[1][0],element[0]] for element in extracted_text if extracted_text]

    return result

def refining(entity_vc_pairs, entity_nv_pairs):
    
    vc_elements = filter.filter_paddle(entity_vc_pairs)

    nv_elements = [(name,val.split(" ",1)) for name,val in entity_nv_pairs ]
    entity_nvc = []
    assigned_coords = []
    for name,val1 in nv_elements:
        for val2, coord in vc_elements:

            if eval(val1[0]) == eval(val2[0]) and val1[1] == val2[1]:
                entity_nvc.append([name," ".join(val1),val1[0],val1[1],coord])
                assigned_coords.append(coord)
                break
        # else:
        #     entity_nvc.append([name," ".join(val1),val1[0],val1[1],[]])
    

    for val2, coord in vc_elements:

        if coord not in assigned_coords:
            entity_nvc.append(["None"," ".join(val2),val2[0],val2[1],coord])
    
    df = pd.DataFrame(entity_nvc, columns=["entity_name","entity_value","value", "unit", "coordinates"])

        
    return df

def process(data: pd.DataFrame,root = "../data/train_images/",is_test = False, save_path = "../data/augmented_train_data.csv"):
    
    print("Processing Train Data Started ------------->")
    data = data.groupby('image_link').agg(list).reset_index(names="image_link")
    processed_data = pd.DataFrame()

    ocr = PaddleOCR(use_angle_cls=True, lang='en',use_gpu=1)
    unprocessed_rows = []
    for index,row in tqdm(data.iterrows(), total=data.shape[0]):
        
        entity_names = row['entity_name']
        entity_values = row['entity_value']

        img = row['image_link']
        group_id = row['group_id'][0]

        img_path = os.path.join(root, img)
        
        try:
            entity_val_cord_pair = extract_texts_with_coordinates(ocr, img_path)
            entity_name_val_pair = list(zip(entity_names,entity_values))

            index_df = refining(entity_val_cord_pair, entity_name_val_pair)
            index_df['image_link'] = img
            index_df['group_id'] = group_id

            processed_data = pd.concat([processed_data,index_df],ignore_index=True)

        except Exception as e:
            print(e)
            unprocessed_rows.append(str(index) + "\n")

    with open("../log/unprocessed_rows.txt","a") as f:
        f.writelines(unprocessed_rows)

    processed_data.to_csv(save_path)
    print("Processing Train Data Finished ------------------>")

    return processed_data
