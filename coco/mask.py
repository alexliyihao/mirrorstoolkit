from .base import _Translater
from .utils import coco_contour_to_cv2
import numpy as np
import cv2
import seaborn as sns
import os
import gc

class MaskInterpreter(_Translater):
    """
    This translater translate pixel-wise class mask into and from
    common objects in Context (COCO, cocodataset.org) label,
    This MaskInterpreter is designed for the project which works on both COCO and
    mask format, e.g. Unet user

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
            sub_masks = [_extract_color(mask, color, label_dictionary, annotation_dict, id+1)
                         for color in color_list if np.any(c)]
            annotations.append(sub_masks)
        # Flatten the 2d array
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
                "segmentation": contours[0].flatten(),
                "image_id": annotation_dict[id], # To be finished
                "iscrowd":0,
                "area": area}
#-------------------------The following is interpreting coco to mask------------------
    def _from_coco(self, dst, coco_data, mode = "color", palette = "viridis"):
        """
        translate the COCO format data to mask format
        Args:
            dst: str, the path output, from memory consideration
                 each individual output will be saved after created
                 rather than saved in the memory
            coco_data: json instance, the complete coco format
            mode: str, in "color" or "category", when outputting the mask, returning
                  3-channel colors, or 1-channel category id representing the color
            palette: str, the palette in seaborn, "viridis" by default
        """
        # check if dst is there, if not create one
        os.makedirs(dst, exist_ok = True)
        # distribute a color for all the categories
        categories = self._extract_categories(coco_data["categories"],
                                              mode = "color",
                                              palette = "viridis")
        path_dict = {}
        # for each image
        for image in coco_data["images"]:
            # create a blank canvas at the same size as canvas
            if mode == "color":
                canvas = np.zeros(image["height"], image["width"], 3)
            else:
                canvas = np.zeros(image["height"], image["width"])
            # filter all the annotation which belongs to this image
            annotations = [annotation in coco_data["annotations"] if annotation["image_id"] = image["id"]]
            for annotation in annotations:
                # for each annotation, draw it on the canvas
                canvas = self._extract_contour(canvas = canvas,
                                               segmentation = annotation["segmentation"],
                                               color = categories[annotation["category_id"]]["color"])

            file_name = self._output_file_name(dst, image)
            # write the image out -- it's for consideration on memory and just in case the
            # dataset might be extremely large
            cv2.imwrite(os.path.join(dst, file_name), canvas)
            # save the file name, with the image_id as the key
            path_dict[image["id"]] = file_name
            # clear the memory(it cleans the memory leak LAST LOOP, but it's okay)
            gc.collect()
        return (dst, path_dict)

    def _output_file_name(self, dst, image):
        """
        generate a output file name
        """
        output_path = f'{image["id"]}_{image["file_name"]}_mask.png'

    def _extract_categories(self, coco_category, mode = "color", palette = "viridis"):
        """
        extract category information from coco_data,
        then assign each category a color

        Args:
            coco_category: json/dict instance, the category data
            mode: str, in "color" or "category", when outputting the mask, returning
                  3-channel colors, or 1-channel category id representing the color
            palette: str, the palette in seaborn, "viridis" by default
        Return:
            color_dict: dict, the dict with their corresponding color and detailed information
        """
        assert mode in ["color", "category"]
        if mode == "color"
            # in color mode, choose a sns palette
            custom_palette = sns.color_palette(palette, len(coco_category))
            # convert it to traditional RGB
            np_palette = np.array(custom_palette)*255
            # give each individual category a color
            coco_category = {category["id"]:{"details":category, "color":np_palette[category["id"]-1]}
                             for category in coco_category}
        else:
            # give each individual category its id as mask
            # give each individual category a color
            coco_category = {category["id"]:{"details":category, "color":category["id"]}
                             for category in coco_category}
        return coco_category

    def _extract_contour(self, canvas, segmentation, color):
        """
        given a cv2 <contour> and a <canvas>, add a mask with <color> on <canvas>
        Args:
            canvas: np.ndarray, in (width,height,3) shape or (width,height),
                    the canvas to be painted on, usually a output from np.zeros
            contour: list[np.ndarray], in (n_point, 1, 2) shape,
                    the contour to be drawed on
            color: iterable with 3 channels, the color to be drawed
        return:
            painted_canvas: np.ndarray, the canvas to be drawed on
        """
        # interpret all the segmentation into cv2
        # this dtype = np.int32 is necessary for running, although it will loss precisions
        segmentation = [coco_contour_to_cv2(contour, dtype = np.int32) for contour in segmentation]
        # for the contour, draw contour on canvas,
        # the first -1 is for draw all contours in the list
        # the last list is for filling the contour
        painted_canvas = cv2.drawContours(canvas, segmentation, -1, color, -1)
