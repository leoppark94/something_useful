from os.path import basename, dirname, split
from glob import glob
import cv2
import json
import numpy as np
from tqdm.notebook import tqdm
import os

def json_reader(json_path):
    '''
    Read JSON
    input Full Path
    '''
    with open(json_path, 'r') as f:
        json_data = json.load(f)
        f.close()
    
    return json_data

def lable_to_minmax_point(json_box):
    """
    input : LabelME Point
    change labelIMG polygon format to [xmin, ymin, xmax, ymax]
    
    return [xmin, ymin, xmax, ymax]
    """
    box_arr = np.array(json_box['points']).T
    xmin = int(np.min(box_arr[0]))
    ymin = int(np.min(box_arr[1]))
    xmax = int(np.max(box_arr[0]))
    ymax = int(np.max(box_arr[1]))
    
    return [xmin, ymin, xmax, ymax]

def one_point_to_xml_form(label_class : str):
    '''
    input : lable name
    output : one labelIMG templete point
    '''
    
    for one_point in point_list:
        if one_point['label'] == label_class:
            one_df_list = list()
            xmin, ymin, xmax, ymax = lable_to_minmax_point(one_point)
            
            result = (result +
                      '\t<object>\n\t\t<name>check</name>\n' +
                      '\t\t<pose>Unspecified</pose>\n' +
                      '\t\t<truncated>0</truncated>\n' +
                      '\t\t<difficult>0</difficult>\n' +
                      '\t\t<bndbox>\n\t\t\t' + 
                      '<xmin>' + str(xmin) + '</xmin>\n\t\t\t' + 
                      '<ymin>' + str(ymin) + '</ymin>\n\t\t\t' +
                      '<xmax>' + str(xmax) + '</xmax>\n\t\t\t' +
                      '<ymax>' + str(ymax) + '</ymax>\n\t\t' + 
                      '</bndbox>\n\t</object>\n')
    return result

def get_label_name(json_point_list):
    # save lable name
    label_name_list = list()
    
    for one_point in json_point_list:
        label_name_list.append(one_point['label'])
        
    label_name_list = list(set(label_name_list))
    
    return label_name_list

def main(json_folder_path : str, img_ext : str, source : str = 'UnKnown', folder_name : str = 'labelme', need_lable : list = []):
    '''
    input
    - json_folder_path : <str> LabelMe JSON label saved folder
                         ex) "D:/Dataset/221116_Kyobo/Labled_Money/"
    - img_ext : <str> like .png .jpg anything that can read in cv2.imread()
    - source : <str> if you want to put source url or something in .xml
    - folder_name : <str> I don't know what this is,,, but XML have it
    '''
    
    # fix path
    if json_folder_path[-1] != '/' or json_folder_path[-1] != '\\':
        json_folder_path = json_folder_path + '/'
    # json glob path
    json_folder_path = json_folder_path + "*.json"
        
    for one_json_path in tqdm(glob(json_folder_path)):

        name = basename(one_json_path).split('.')[0] + img_ext
        folder_path = os.path.split(one_json_path)[0]
        file_full_path = folder_path + '/' + name
        xml_name = basename(one_json_path).split('.')[0] + '.xml'
        # get img shape
        img = cv2.imread(file_full_path)
        height, width, depth = img.shape
        result = ('<annotation>\n\t<folder>' + 
                  folder_name + '</folder>\n\t<filename>' + 
                  name + '</filename>\n\t<path>'+ 
                  file_full_path +'</path>\n\t<source>\n\t\t<database>' +
                  source + '</database>\n\t</source>\n\t<size>\n\t\t<width>' + 
                  str(width) + '</width>\n\t\t<height>' + 
                  str(height) + '</height>\n\t\t<depth>' + 
                  str(depth) + '</depth>\n\t</size>\n\t<segmented>0</segmented>\n')

        point_list = json_reader(one_json_path)['shapes']
        label_class_list = get_label_name(point_list)
        
        if need_lable != []:
            label_class_list = need_lable
        
        # try to append relative classes
        for one_class_name in label_class_list:
            for one_point in point_list:
                if one_point['label'] == one_class_name:
                    xmin, ymin, xmax, ymax = lable_to_minmax_point(one_point)
                    result = (result + '\t<object>\n\t\t<name>' +
                              one_class_name + '</name>\n\t\t<pose>Unspecified</pose>\n\t\t<truncated>0</truncated>\n' +
                          '\t\t<difficult>0</difficult>\n\t\t<bndbox>\n\t\t\t' + 
                          '<xmin>' + str(xmin) + '</xmin>\n\t\t\t' + 
                          '<ymin>' + str(ymin) + '</ymin>\n\t\t\t' +
                          '<xmax>' + str(xmax) + '</xmax>\n\t\t\t' +
                          '<ymax>' + str(ymax) + '</ymax>\n\t\t' + 
                          '</bndbox>\n\t</object>\n')

        result = result + '</annotation>\n'
        result_f = open(folder_path + '/' + xml_name,'w')
        result_f.write(result)
        result_f.close()