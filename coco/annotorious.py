from .base import _Translater
from .utils import coco_contour_to_cv2
import re
import cv2

class AnnotoriousInterpreter(_Translater):
    """
    This translater translate Annotorious(https://recogito.github.io/annotorious/)
    annotation into and from common objects in Context (COCO, cocodataset.org) label
    This method is modified from https://github.com/alexliyihao/auto-annotation-web
    """
    def _set_meta():
        """
        set the meta setting of this translator
        The variables below are necessary but feel free to play with anything else.
        """
        self.format_name = "Annotorious"

    def _validate_new_format(self, data):
        """
        validate the if the <data> is readable for Annotorious
        Args:
            data: list[json], a list of annotorious annotations
        Return:
            if <data> is interpretable in <format>, return true
            else raise a AssertionError, ValueError, TypeError or KeyError
        """
        return all([self._validate_annotorious_individual(self._dejsonized(annotation))
                    for annotation in data])

    def _validate_annotorious_individual(self,data):
        """
        individually check if each individual annotation is Annotorious format
        """
        try:
            assert data["type"] == "Annotation"
            assert data["body"]
            assert data["target"]
            assert data["target"]["selector"]["type"] == "SvgSelector"
            assert data["target"]["selector"]["value"]
        except (AssertionError, KeyError):
            raise
        else:
            return True

    def _to_coco(self, data):
        """
        translate the annotorious annotations to COCO format
        """
        categories = {}
        annotations = []
        images = self._image_processor()

        for annotation in data:
            label = self._get_label(annotation)
            if label not in categories.keys():
                categories[label] = len(categories)+1
            category_id = categories[label]
            contour_numeric, area, bbox = self._process_contour(annotation)
            annotations.append({
                "segmentation": [contour_numeric],
                "area": area,
                "iscrowd": 0,
                "image_id": 0,#TBF here
                "bbox": bbox,
                "category_id": category_id,
                "id": 0 #TBF here
            })
        categories = self._tidy_categories(categories)
        return {
                "images":images,
                "annotations": annotations,
                "categories": categories
                }

    def _file_manager(self):
        """
        To be finish: how should I encode with all the images?
        Args:
            data: iterable(list[image], list[annotations]) all the data,
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
        return [{"supercategory":category, "id": id,"name": category}
                for category, id in categories.items()]

    def _get_label(self, annotation):
        """
        for a individual annotation, get the which is saved as "tagging"
        args:
            annotation: dict(json), a individual annotorious annotation
        return:
            label, list[str] the content in the tagging
        """
        word_body = annotation["body"]
        tagging_list = [text_body["value"] for text_body in word_body
                        if text_body["purpose"] == "tagging"
                        ]
        return tagging_list[0]

    def _process_contour(self, annotation):
        # get the svg coordinate string
        contour_string = annotation['target']["selector"]["value"]
        # convert the string, I rounded the digit to 2 digit decimal,
        # from the tradition of COCO officially release
        contour_numeric = [round(float(i),2) for i in re.findall(r"[0-9]+.[0-9]+", contour_string)]
        # reorganize them into points format, and convert it into a contour
        points = coco_contour_to_cv2(contour_numeric, dtype = np.float32)
        # compute the area -- dtype = float32 is necessary for the following
        # is not working with float64 or double
        area, bbox = self._area_and_bbox(points)
        return contour_numeric, area, bbox


    def _from_coco(self, data):
        """
        translate the COCO format data to the annotorious annotations format
        """
        pass
