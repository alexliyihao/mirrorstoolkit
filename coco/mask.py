from .base import _Translater

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
        self.format_name = "new_format_name"

    def _validate_new_format(self, data):
        """
        please override this:
        validate the if the <data> is readable for <format>
        Args:
            data: json,numpy array, or whatever other future format the data input
            format: str, should be defined in self.format_string
        Return:
            if <data> is interpretable in <format>, return true
            else raise a ValueError
        """
        pass

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
