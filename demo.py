'''
Demo code for the paper

Choy et al., 3D-R2N2: A Unified Approach for Single and Multi-view 3D Object
Reconstruction, ECCV 2016
'''
import os
import sys
if (sys.version_info < (3, 0)):
    raise Exception("Please follow the installation instruction on 'https://github.com/chrischoy/3D-R2N2'")
sys.path.append('../../vision/reconstruction_3d/R2N2/')
import shutil
import numpy as np
from subprocess import call
import cv2
from PIL import Image
from models import load_model
from lib.config import cfg, cfg_from_list
from lib.solver import Solver
from lib.voxel import voxel2obj

DEFAULT_WEIGHTS = '../../vision/reconstruction_3d/R2N2/weights/ResidualGRUNet.npy'


def cmd_exists(cmd):
    return shutil.which(cmd) is not None


# def download_model(fn):
#     if not os.path.isfile(fn):
#         # Download the file if doesn't exist
#         print('Downloading a pretrained model')
#         call(['wget', 'http://cvgl.stanford.edu/data2/ResidualGRUNet.npy',
#               '--create-dirs', '-o', fn])


def load_images(img1, img2):
    ims = []
    # for i in range(1, 3):
    #     im = Image.open(os.path.join(img_folder_path, '%d.png'% i))

    #crop and resize
    center = img1.shape
    w, h = 1200, 1080
    x = center[1]/2 - w/2
    y = center[0]/2 - h/2

    crop_img1 = img1[int(y):int(y+h), int(x):int(x+w)]
    crop_img1 = cv2.resize(crop_img1, (127, 127))

    crop_img2 = img2[int(y):int(y+h), int(x):int(x+w)]
    crop_img2 = cv2.resize(crop_img2, (127, 127))

    ims.append([np.array(crop_img1).transpose(
        (2, 0, 1)).astype(np.float32) / 255.])
    ims.append([np.array(crop_img2).transpose(
        (2, 0, 1)).astype(np.float32) / 255.])
    return np.array(ims)


def create_voxel_object(img1, img2, pred_file_name):

    # Set the batch size to 1
    cfg_from_list(['CONST.BATCH_SIZE', 1])

    # load images
    demo_imgs = load_images(img1, img2)

    # Download and load pretrained weights
    # download_model(DEFAULT_WEIGHTS)

    # Use the default network model
    NetClass = load_model('ResidualGRUNet')

    # Define a network and a solver. Solver provides a wrapper for the test function.
    net = NetClass(compute_grad=False)  # instantiate a network
    net.load(DEFAULT_WEIGHTS)                        # load downloaded weights
    solver = Solver(net)                # instantiate a solver

    # Run the network
    voxel_prediction, _ = solver.test_output(demo_imgs)

    # Save the prediction to an OBJ file (mesh file).
    voxel2obj(pred_file_name, voxel_prediction[0, :, 1, :, :] > cfg.TEST.VOXEL_THRESH)

    # Use meshlab or other mesh viewers to visualize the prediction.
    # For Ubuntu>=14.04, you can install meshlab using
    # `sudo apt-get install meshlab`
    # if cmd_exists('meshlab'):
    #     call(['meshlab', pred_file_name])
    # else:
    #     print('Meshlab not found: please use visualization of your choice to view %s' %
    #           pred_file_name)
