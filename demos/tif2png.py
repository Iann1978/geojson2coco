import cv2
import numpy as np
import os




def convert_one_file(src_pathfile, dst_pathfile) :
    img = cv2.imread(src_pathfile, cv2.IMREAD_ANYDEPTH|cv2.IMREAD_COLOR)

    img2 = img.astype(np.float32)
    img3 = img2 / 1024 * 255
    img4 = np.clip(img3, 0, 255)
    img5 = img4.astype(np.uint8)

    cv2.imwrite(dst_pathfile, img5)

    print(np.min(img), np.max(img))

    # cv2.imshow('tif2png', img5)
    # cv2.waitKey()



def convert_one_folder(src_folder, dst_folder) :
    for root, dirs, files in os.walk(src_folder):

        src_path_list = [os.path.join(root, f) for f in files if f.endswith('.tif')]
        dst_path_list = [os.path.join(dst_folder, f.replace('.tif', '.png')) for f in files if f.endswith('.tif')]

        pair_list = zip(src_path_list, dst_path_list)
        for src_pathfile, dst_pathfile in pair_list:
            convert_one_file(src_pathfile, dst_pathfile)

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='./src_folder', help='')
    parser.add_argument('--output', type=str, default='./dst_folder', help='')
    opt = parser.parse_args()

    convert_one_folder(opt.input, opt.output)

    print('Succeed!')