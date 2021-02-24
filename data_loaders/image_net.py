import os
import numpy as np
import matplotlib.image as mpimg
import torch
from torch.utils.data import Dataset

class ImageNetDataset(Dataset):
    """
    A DataLoader for ImageNet Dataset designed specifically for KU HPC Cluster.
    """
    labels_dir = '/datasets/ImageNet/ILSVRC2015/devkit/data'
    train_labels_file = 'map_clsloc.txt'
    valid_labels_file = 'ILSVRC2015_clsloc_validation_ground_truth.txt'
    train_labels_path = os.path.join(labels_dir, train_labels_file)
    valid_labels_path = os.path.join(labels_dir, valid_labels_file)
    train_data_dir = '/datasets/ImageNet/ILSVRC2015/Data/CLS-LOC/train'
    valid_data_dir = '/datasets/ImageNet/ILSVRC2015/Data/CLS-LOC/val'
    
    def __init__(self, train: bool, transform=None):

        self.transform = transform
        
        self.class_id_to_index = {}
        self.class_index_to_name = {}
        self.class_name_to_index = {}
        self.train = train
        
        # store labels
        self.labels = []
        # store paths to images
        self.data = []
        
        # get classed mapping
        train_f = open(self.train_labels_path, "r") 
        for line in train_f:
            ID, index, name = line[:-1].split(' ')
            index = int(index)
            self.class_id_to_index[ID] = index
            self.class_index_to_name[index] = name
            self.class_name_to_index[name] = index
        
        if train:
            train_data_folders = os.listdir(self.train_data_dir)
            for ID in train_data_folders:
                label = self.class_id_to_index[ID]
                label_path = os.path.join(self.train_data_dir, ID)
                for data_file in os.listdir(label_path):
                    self.data.append(os.path.join(label_path, data_file))
                    self.labels.append(label)
        else:
            valid_f = open(self.valid_labels_path, "r")
            for line in valid_f:
                self.labels.append(int(line[:-1]))
            for data_file in sorted(os.listdir(self.valid_data_dir)):
                self.data.append(os.path.join(self.valid_data_dir, data_file))
            
            
    def __len__(self):
        return len(self.labels)
        
    def __getitem__(self, index):
        
        label = self.labels[index]
        data_path = self.data[index]
        data = mpimg.imread(data_path)
        
        # some images might have 1 channel
        if len(data.shape) < 3:
            H, W = data.shape
            data_temp = data.copy()
            data = np.zeros((H, W, 3))
            for i in range(3):
                data[:,:,i] = data_temp
            
            data = data.astype(np.uint8)
        if self.transform:
            data = self.transform(data)
        
        return data, label
        