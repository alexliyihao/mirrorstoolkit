class _Translater(object):
    """
    base class of all the translators
    All the inheritance please override _set_meta(), _validate_new_format()
    _to_coco(), and _from_coco() methods, then the class is ready to be called in
    to_coco() and from_coco public methods
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
            else raise a ValueError
        """
        pass

    def _to_coco(self, data):
        """
        please override this:
        translate the data to COCO format
        Args:
            data: json,numpy array, or whatever other future format the data input
        Return:
            coco_output: json, the coco-format annotations
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
            data: json or whatever other future format the data input
        Return:
            if <data> is interpretable in as coco, return true else return false
        """
        pass

    def to_coco(self, data):
        """
        The wrapper including the complete procedure translating the data to COCO
        please be noticed that data is ONE parameter
        """
        try:
            self._validate_new_format(data)
        except ValueError:
            print(f"The data imported in not recogized as {self.format_name}")
            return 1
        else:
            coco_output = self._to_coco(data)
            return coco_output


    def from_coco(self, data):
        """
        The wrapper including the complete procedure
        translating COCO to specific format
        """
        try:
            self._validate_coco(data)
        except ValueError:
            print(f"The data imported in not recogized as COCO format")
            return 1
        else:
            format_output = self._from_coco(data)
            return format_output
