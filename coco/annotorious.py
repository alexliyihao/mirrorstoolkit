from .base import _Translater
from .utils import coco_contour_to_cv2
import re
import cv2
import json
import gc

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

#-------------------------The following is interpreting coco to annotorious------------------

    def _from_coco(self, dst, coco_data):
        """
        translate the COCO format data to the annotorious annotations format
        """
        # check if dst is there, if not create one
        os.makedirs(dst, exist_ok = True)
        # distribute a color for all the categories
        category_dict = self._extract_categories(coco_data["categories"])
        # generate a path dict for output
        path_dict = {}
        # for each image
        for image in coco_data["images"]:
            # filter all the annotation which belongs to this image
            annotations = [annotation in coco_data["annotations"] if annotation["image_id"] = image["id"]]
            # translate all the related annotations into jsons
            annotation_jsons = [anno for annotation in annotations for anno in self._interpret_annotation(annotation, category_dict)]
            # define the output path
            file_name = self._output_file_name(dst, image)
            with open(os.path.join(dst, file_name), 'w') as output:
                json.dump(data, output, ensure_ascii=False)
            path_dict[image["id"]] = file_name
            gc.collect()
        return (dst, path_dict)

    def _output_file_name(self, dst, image):
        """
        generate a output file name
        """
        output_path = f'{image["id"]}_{image["file_name"]}.w3c.json'

    def _extract_categories(self, coco_category):
        """
        extract category information from coco_data for fast access
        Args:
            coco_category: json/dict instance, the category data
        Return:
            category_dict: dict, the dict key is category id, and value is category_name
        """
        return {category["id"]:category["name"]} for category in coco_category}

    def _interpret_annotation(self, annotation, category_dict):
        """
        given a COCO annotation segmentation (one annotation in ["annotation"]),
        translate the format to a readable svg selector string
        args:
            contour: list, the segmentation contour of the annotation
        returns:
            polygon: string, the svg selector in Annotorious form
        """
        segmentation = annotation['segmentation']
        category_name = category_dict[annotation['category_id']]
        # each annotation may have more than one contours in their segmentation field
        polygon_strings = [self._formatting_annotation(contours, category_name) for contours in segmentation]
        return polygon_strings

    def _formatting_annotation(self, contour, category_name):
        """
        formatting the annotation output into W3C Annotorious format
        the class label should be in TextualBody - tagging
        The svg selector string is from self._interpret_polygon()
        """
        return {
            "type": "Annotation",
            "body":[
            {"type": "TextualBody", "value": category_name, "purpose": "tagging"}
            ],
            "target":{"selector":
            {"type": "SvgSelector",
             "value": self._interpret_polygon(contour)}
            },
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": "#725470be-7239-4e17-9850-48583eb7c2a5"
        }

    def _interpret_polygon(self, contour):
        """
        given a COCO annotation segmentation (one contour in ["segmentation"]),
        translate the format to a readable svg selector string
        args:
            contour: list, the segmentation contour of the annotation
        returns:
            polygon: string, the svg selector in Annotorious form
        """
        contour = [[contour[2*i], contour[2*i+1]] for i in range(int(len(contour)/2))]
        points = " ".join([",".join([str(points[0]), str(points[1])]) for points in contour])
        prefix = '"<svg><polygon points=\\"'
        suffix = '\\"/></svg>"'
        return f"{prefix}{points}{suffix}"
