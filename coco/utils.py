import numpy as np

def coco_contour_to_cv2(contour, dtype):
    """
    translate coco format [x_1,y_1,x_2,y_2,...]
    to opencv contour [[[x_1,y_1]], [[x_2,y_2]],...]
    args:
        contour: list, the coco format contour
        dtype: the dtype of output needed, cv2 is a little bit weird on the dtype
    """
    return np.array([[[contour[2*i], contour[2*i+1]]]
                      for i in range(int(len(contour)/2))],
                      dtype = dtype)
