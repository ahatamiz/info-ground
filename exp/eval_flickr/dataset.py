import os
import numpy as np
import random
from copy import deepcopy
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.dataloader import default_collate

import utils.io as io
from utils.constants import Constants
from global_constants import flickr_paths


class FlickrDatasetConstants(Constants):
    def __init__(self,subset):
        super().__init__()
        self.subset = subset
        self.det_dir = os.path.join(flickr_paths['det_dir'],self.subset)
        self.image_dir = flickr_paths['image_dir']

        self.image_ids_txt = os.path.join(
            flickr_paths['downloads_dir'],
            flickr_paths['subsets'][self.subset])
        self.phrase_boxes_json = os.path.join(
            flickr_paths['proc_dir'],
            flickr_paths['phrase_boxes'][self.subset])
        self.sentences_json = os.path.join(
            flickr_paths['proc_dir'],
            flickr_paths['sentences'][self.subset])
        
        self.boxes_hdf5 = os.path.join(self.det_dir,'boxes.hdf5')
        self.features_hdf5 = os.path.join(self.det_dir,'features.hdf5')
        self.labels_hdf5 = os.path.join(self.det_dir,'labels.hdf5')
        self.scores_hdf5 = os.path.join(self.det_dir,'scores.hdf5')

        self.max_objects = 30  


class FlickrDataset(Dataset):
    def __init__(self,const):
        super().__init__()
        self.const = deepcopy(const)
        self.image_ids = self.read_image_ids()
        self.phrase_boxes = io.load_json_object(self.const.phrase_boxes_json)
        self.sentences = io.load_json_object(self.const.sentences_json)
        os.environ['HDF5_USE_FILE_LOCKING']="FALSE"

    def read_image_ids(self):
        image_ids = io.read(self.const.image_ids_txt)
        image_ids = [idx.decode() for idx in image_ids.split()]
        return image_ids

    def get_image_path(self,image_id):
        return os.path.join(
            self.const.image_dir,
            f'{image_id}.jpg')
            
    def __len__(self):
        return 5*len(self.image_ids)

    def get_caption(self,image_id,cap_num):
        return self.sentences[image_id][cap_num]['sentence']

    def get_phrases(self,image_id,cap_num):
        return self.sentences[image_id][cap_num]['phrases']

    def get_gt_boxes(self,image_id):
        return self.phrase_boxes[image_id]

    def read_object_features(self,image_id):
        f = io.load_h5py_object(self.const.features_hdf5)
        features = f[image_id][()]
        f.close()
        return features

    def read_object_boxes(self,image_id):
        f = io.load_h5py_object(self.const.boxes_hdf5)
        boxes = f[image_id][()]
        f.close()
        return boxes

    def pad_object_features(self,features):
        T,D = features.shape # num_objects x feat. dim
        pad_mask = np.zeros(self.const.max_objects).astype(np.bool)
        if T==self.const.max_objects:
            return features, pad_mask

        if T > self.const.max_objects:
            features = features[:self.const.max_objects]
        else:
            features = np.concatenate((
                features,
                np.zeros([self.const.max_objects-T,D])),0).astype(np.float32)
            pad_mask[T:] = True
            
        return features, pad_mask

    def __getitem__(self,i):
        image_num = i//5
        cap_num = i%5
        image_id = self.image_ids[image_num]
        caption = self.get_caption(image_id,cap_num)
        phrases = self.get_phrases(image_id,cap_num)
        features = self.read_object_features(image_id)
        features, pad_mask = self.pad_object_features(features)
        boxes = self.read_object_boxes(image_id)
        gt_boxes = self.get_gt_boxes(image_id)
        to_return = {
            'image_id': image_id,
            'cap_num': cap_num,
            'caption': caption,
            'phrases': phrases,
            'features': features,
            'boxes': boxes,
            'gt_boxes': gt_boxes,
            'pad_mask': pad_mask,
        }
        return to_return


if __name__=='__main__':
    const = FlickrDatasetConstants('val')
    dataset = FlickrDataset(const)
    print(len(dataset),len(dataset)//5,5*(len(dataset)//5))
    import pdb; pdb.set_trace()