from .base import _Translater

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
            else raise a ValueError
        """
        pass

    def _to_coco(self, data):
        """
        translate the annotorious annotations to COCO format
        """
        pass

    def _from_coco(self, data):
        """
        translate the COCO format data to the annotorious annotations format
        """
        pass
