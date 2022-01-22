from .base import _Translater
import numpy as np

class MaskInterpreter(_Translater):
    """
    This translater translate pixel-wise class mask into and from
    common objects in Context (COCO, cocodataset.org) label
    This method is generalized from https://github.com/alexliyihao/AAPI_code
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


    def _to_coco(self):
        """
        please override this:
        translate the data to COCO format
        """
        pass

    def _from_coco(self):
        """
        please override this:
        translate the COCO format data to other format
        """
        pass
