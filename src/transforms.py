import os
import torch
import random
import numpy as np
import torch.nn.functional as F

from torchvision.io import read_image
from torchvision.utils import save_image
from torchvision.transforms import (Resize,
                                   RandomHorizontalFlip, RandomVerticalFlip, RandomRotation,
                                   Normalize, AutoAugment)

__all__ = ["ReadImaged", "ResizeImaged", "AutoAugmentd", "NormalizeImaged"]


class BaseTransform(object):
    def __init__(self, keys, **kwargs):
        self.keys = keys
        self._parseVariables(**kwargs)

    def __call__(self, data, **kwargs):
        for key in self.keys:
            if key in data:
                data[key] = self._process(data[key], **kwargs)
            else:
                raise KeyError(f"{key} is not a key in data.")

        return data

    def _parseVariables(self, **kwargs):
        pass

    def _process(self, single_data, **kwargs):
        NotImplementedError

    def _update_prob(self, cur_ep, total_ep):
        pass


class ReadImaged(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(ReadImaged, self).__init__(keys, **kwargs)

    def _process(self, single_data, **kwargs):
        single_data = read_image(single_data)
        return single_data


class MirrorPaddingd(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(MirrorPaddingd, self).__init__(keys, **kwargs)

    def _process(self, single_data, **kwargs):
        _, h, w = single_data.shape
        if h == w:  return single_data

        max_len = max(h, w)
        if h == max_len:  # h > w
            w_pad = max_len - w
            w_pad_half = w_pad // 2
            pad_size = (w_pad_half, w_pad-w_pad_half, 0, 0)
        else:  # w > h
            h_pad = max_len - h
            h_pad_half = h_pad // 2
            pad_size = (0, 0, h_pad_half, h_pad-h_pad_half)
        
        pad_image = F.pad(single_data.float(), pad_size, 'reflect')

        return pad_image.to(torch.uint8)


class ResizeImaged(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(ResizeImaged, self).__init__(keys, **kwargs)

    def _parseVariables(self, **kwargs):
        self.resize = Resize(kwargs.get('size'))

    def _process(self, single_data, **kwargs):
        return self.resize(single_data)


class RandomFlipRot90(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(RandomFlipRot90, self).__init__(keys, **kwargs)

    def _parseVariables(self, **kwargs):
        self.hflip = RandomHorizontalFlip(p=0.5)
        self.vflip = RandomVerticalFlip(p=0.5)
        self.rot90 = RandomRotation((90, 90))

    def _process(self, single_data, **kwargs):
        x = self.hflip(single_data)
        x = self.vflip(x)
        if random.random() < 0.5:
            x = self.rot90(x)

        return x


class AutoAugmentd(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(AutoAugmentd, self).__init__(keys, **kwargs)

    def _parseVariables(self, **kwargs):
        self.p = kwargs.get('prob')
        self.autoaug = AutoAugment()

    def _process(self, single_data, **kwargs):
        if random.random() < self.p:
            return self.autoaug(single_data)
        else:
            return single_data


class NormalizeImaged(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(NormalizeImaged, self).__init__(keys, **kwargs)

    def _parseVariables(self, **kwargs):
        mean = (0.485, 0.456, 0.406)
        std = (0.229, 0.224, 0.225)
        self.normal = Normalize(mean, std)

    def _process(self, single_data, **kwargs):
        return self.normal(single_data.float())


class VisualizeImaged(BaseTransform):
    def __init__(self, keys, **kwargs):
        super(VisualizeImaged, self).__init__(keys, **kwargs)
        self.count = 0
    
    def _process(self, single_data, **kwargs):
        os.makedirs('./tmp', exist_ok=True)
        save_image(single_data / 255, f'./tmp/visual_image_{self.count}.jpg')
        self.count += 1
        print(single_data.shape)
        exit()
        
        return single_data


if __name__ == '__main__':
    pass
