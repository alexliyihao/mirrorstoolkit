import json
from datatime import datetime
import json
import os

class ValidationError(ValueError):
    pass

class _Translater(object):
    """
    base class of all the translators convert annotation into and from
    common objects in Context (cocodataset.org) object-detection/stuff
    segmentation label

    All the inheritance please override _set_meta(), _validate_new_format()
    _to_coco(), _from_coco(), and _file_manager() methods, then the class is ready to be called in
    to_coco() and from_coco() public methods, all exceptions are solved internally
    """

    def __init__(self):
        """
        initialization of the class
        """
        self._set_meta()

    def _set_meta():
        """
        please override this: set the meta setting of this translator
        The variables below are necessary but feel free to play with anything else.
        """
        self.format_name = "new_format_name"

    def _validate_new_format(self, data):
        """
        please override this:
        validate the if the <data> is readable for the new format
        Args:
            data: json,numpy array, or whatever other future format the data input
        Return:
            if <data> is interpretable in <format>, return true
            else raise a AssertionError, ValueError or KeyError
        """
        pass

    def _to_coco(self, data):
        """
        please override this:
        translate the data to COCO format
        You don't need to provide "info" field, the translater will start a guide itself
        Args:
            data: json,numpy array, or whatever other future format the data input
        Return:
            coco_output: json(dict), the coco-format annotations
        """
        pass

    def _from_coco(self, data):
        """
        please override this:
        translate the COCO format data to other format
        Args:
            data: json, the coco-format annotations
        Return:
            format_output: json,numpy array, or whatever other future format the data input
        """
        pass

    def _validate_coco(self, data):
        """
        validate the if the <data> is readable as a coco format
        Args:
            data: json string or dictionary
        Return:
            if <data> is interpretable in COCO, return true
            else raise a AssertionError, ValueError or KeyError
        """
        data = self._dejsonized(data)
        try:
            assert data["info"]
            assert data["images"]
            assert data["annotations"]
            assert data["categories"]
            # Most of our dataset are not with licenses during development, it's on you
            #assert data["licenses"]
        except (AssertionError, KeyError) as e:
            raise ValidationError(f"There're some data not acceptable as COCO format: {repr(e)}")
        else:
            return True

    def _dejsonized(self, data):
        """
        helper function that automatically unify the data type:
        if data is a str (which expected from a web json),
        automatically load it as a dict, and pass the dict if it is.
        Else it will raise a TypeError
        """
        if isinstance(data, str):
            return json.loads(data)
        elif isinstance(data, dict):
            return data
        else:
            raise TypeError(f"{type(data)}")

    def validate_new_format(self, data):
        """
        wrapper of _validate_new_format
        if the <data> is readable for the new format
        Args:
            data: json,numpy array, or whatever other future format the data input
        Return:
            if <data> is interpretable in <format>, return true
            else raise a ValidationError
        """
        try:
            self._validate_new_format(data)
        except(AssertionError, ValueError, KeyError, TypeError) as e:
            raise ValidationError(f"There're some data not acceptable as {self.format_name} format: {repr(e)}")

    def _coco_meta(self):
        """
        prepare a meta information for COCO format
        """
        now = datetime.now()
        version = input("Please give a version code: ")
        contributor = input("Please give a contributor name")
        url = input("Please give a url to the dataset")
        return {
                "year": now.strftime("%Y"),
                "version": version,
                "description": "Exported from Mirrorstoolkit",
                "contributor": contributor,
                "url": url,
                "date_created": now.strftime("%Y-%M-%dT%H:%M:%S")
            }

    def _coco_licenses_prepraration(self, path = None):
        """
        Prepare the license field
        if a json file path is not given, a by-nc-sa license is given as default
        """
        if path == None:
            return  {"url": "http://creativecommons.org/licenses/by-nc-sa/2.0/",
                     "id": 1,
                     "name": "Attribution-NonCommercial-ShareAlike License"
                    }
        else:
            try:
                assert os.path.splitext(path)[1] == ".json"
            except AssertionError:
                print("The license file is not a valid json file")
            else:
                return json.load(path)

    def _area_and_bbox(self, contours):
        """
        utility functions compute the area and bounding boxes
        args:
            points, list[list[float,float]], the points of the contour
        """
        # compute the area -- dtype = float32 is necessary for the following
        # is not working with float64 or double
        area = cv2.contourArea(np.array(points, dtype = np.float32))
        # bounding box, please be noticed that it's [x,y,w,h] format
        bbox = cv2.boundingRect(np.array(points, dtype = np.float32))
        return area, bbox

    def to_coco(self, data, license_file, **kwargs):
        """
        The wrapper including the complete procedure translating the data to COCO
        please be noticed that data is ONE parameter
        """
        try:
            self.validate_new_format(data)
        except ValidationError as e:
            return str(e)
        else:
            coco_output = self._to_coco(data,license_file,**kwargs)
            coco_output["info"] = self._coco_meta()
            coco_output["licenses"] = self._coco_licenses_prepraration(license_file)
            return coco_output

    def from_coco(self, dst, data, **kwargs):
        """
        The wrapper including the complete procedure
        translating COCO to specific format
        """
        try:
            self._validate_coco(data)
        except ValidationError as e:
            return str(e)
        else:
            format_output = self._from_coco(dst,data,**kwargs)
            return format_output
