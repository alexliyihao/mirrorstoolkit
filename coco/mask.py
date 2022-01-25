from .base import _Translater
import numpy as np
from PIL import Image
import cv2

class MaskInterpreter(_Translater):
    """
    This translater translate pixel-wise class mask into and from
    common objects in Context (COCO, cocodataset.org) label

    This method is generalized from https://github.com/alexliyihao/AAPI_code
    and is inspired by https://www.immersivelimit.com/create-coco-annotations-from-scratch,
    the re-implementation optimized the efficiency and dependent packages
    """
    def _set_meta():
        """
        please override this: set the meta setting of this translator
        The variables below are necessary but feel free to play with anything else.
        """
        self.format_name = "pixel mask"

    def _validate_new_format(self, data):
        """
        please override this:
        validate the if the <data> is readable for <format>
        Args:
            data: tuple(img, mask, dictionary)
                  img and mask are supposed to be np.ndarray
                  or some format can be translated by np.array(img) and np.array(mask)
                  dictionary are supposed to be dict
        Return:
            if <data> is interpretable in <format>, return true
            else raise a AssertionError
        """
        #extract img
        imgs = data[0]
        # if it's not a np.ndarray, convert it, most of the times it's not hard...
        if not isinstance(imgs, np.ndarray):
            imgs = np.array(imgs)
        # extract mask
        masks = data[1]
        # if it's not a np.ndarray, convert it, most of the times it's not hard...
        if not isinstance(masks, np.ndarray):
            masks = np.array(masks)

        # assert all pixels are labeled
        assert imgs.shape == masks.shape

        # extract dictionary
        label_dictionary = data[2]
        assert isinstance(label_dictionary, dict)

        # assert that all the labels in the mask are in the dictionary
        # Please be noticed that the reverse is not supposed to be always true
        labels_used = np.unique(masks)
        for i in labels_used:
            assert i in label_dictionary.keys()

        return True


    def _to_coco(self, data):
        """
        translate the mask data to COCO format
        """
        # the data is supposed to be passed in as a iterable
        imgs, masks, label_dictionary = data
        annotations = []
        images, annotation_dict = self._to_coco_file_manage()
        categories = self._tidy_categories(label_dictionary)
        annotations = self._translate_mask(masks, label_dictionary, annotation_dict)
        return {
                "images":images,
                "annotations": annotations,
                "categories": categories
                }

    def _to_coco_file_manage(self):
        """
        To be finish: how should I encode with all the images?
        Args:
            data: iterable(image, mask, annotations) all the data,
        Return:
            list[dict]: the "image" field of the coco format
            dict{int,int}: the 1-many correspondence between image and annotations
        {
        "license": 4,
        "file_name": "000000397133.jpg",
        "coco_url": "http://images.cocodataset.org/val2017/000000397133.jpg",
        "height": 427,
        "width": 640,
        "date_captured": "2013-11-14 17:02:52",
        "flickr_url": "http://farm7.staticflickr.com/6116/6255196340_da26cf2c9e_z.jpg",
        "id": 397133
        },
        """
        return [],{}

    def _tidy_categories(self, categories):
        """
        re-format categories dictionary, this funtion might need later modification
        """
        # current setting:
        # each label is set as a supercategory,
        # the sub-category share its name with supercategory
        return [{"supercategory":category, "id": id+1, "name": category}
                for id, category in dict(enumerate(a.values())]

    def _translate_mask(masks, label_dictionary, annotation_dict):
        """
        wrapper extract all the masks information
        To be finished: how to deal with the 1-1 correspondence between the images and masks?
        """
        annotation_complete = []
        for id, mask in enumerate(masks):
            color_list = self._unique_color(mask)
            # for any color except [0,0,0], extract the contour and other information
            sub_masks = [_extract_color(mask, color, label_dictionary, annotation_dict, id)
                         for color in color_list if np.any(c)]
            annotations.append(sub_masks)
        return [annotation for mask_groups in annotation_complete for annotation in mask_groups]

    def _unique_color(self, img):
        """
        helper function of _translate_mask(),
        get all the unique colors in a np.ndarray
        Args:
            img: np.ndarray, the image
        Returns:
            np.ndarray, an array including all the individual colors
        """
        return np.unique(img.reshape(-1, img.shape[2]), axis=0)

    def _extract_color(mask, color, label_dictionary, annotation_dict, id):
        """
        helper function of _translate_mask(),
        extract the information of a specific <color> in <mask> and <label_dictionary>
        """
        # extract boolean masks of this specific color as uint8(output for cv2.threshold)
        sub_mask = np.all(img == color, axis = -1).astype("uint8")
        # find the contour
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # compute the area and bbox
        area, bbox = _area_and_bbox(contours[0])
        return {"bbox": bbox,
                "category_id": label_dictionary[color],
                "segmetation": contours[0].flatten(),
                "image_id": annotation_dict[id], # To be finished
                "iscrowd":0,
                "area": area}

    def _from_coco(self):
        """
        please override this:
        translate the COCO format data to other format
        """
        pass
