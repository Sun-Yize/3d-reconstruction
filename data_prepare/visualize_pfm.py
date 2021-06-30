import re
import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt


def load_pfm(file):
    header = file.readline().decode('UTF-8').rstrip()

    if header == 'PF':
        color = True
    elif header == 'Pf':
        color = False
    else:
        raise Exception('Not a PFM file.')
    dim_match = re.match(r'^(\d+)\s(\d+)\s$', file.readline().decode('UTF-8'))
    if dim_match:
        width, height = map(int, dim_match.groups())
    else:
        raise Exception('Malformed PFM header.')
    scale = float((file.readline()).decode('UTF-8').rstrip())
    if scale < 0:
        data_type = '<f'
    else:
        data_type = '>f'
    data_string = file.read()
    data = np.fromstring(data_string, data_type)
    shape = (height, width, 3) if color else (height, width)
    data = np.reshape(data, shape)
    data = cv2.flip(data, 0)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('depth_path')
    args = parser.parse_args()
    depth_path = args.depth_path
    if depth_path.endswith('npy'):
        depth_image = np.load(depth_path)
        depth_image = np.squeeze(depth_image)
        print('value range: ', depth_image.min(), depth_image.max())
        plt.imshow(depth_image, 'rainbow')
        plt.show()
    elif depth_path.endswith('pfm'):
        depth_image = load_pfm(open(depth_path, 'rb'))
        ma = np.ma.masked_equal(depth_image, 0.0, copy=False)
        print('value range: ', ma.min(), ma.max())
        plt.imshow(depth_image, 'rainbow')
        plt.show()
    else:
        depth_image = cv2.imread(depth_path)
        ma = np.ma.masked_equal(depth_image, 0.0, copy=False)
        print('value range: ', ma.min(), ma.max())
        plt.imshow(depth_image)
        plt.show()
