import PIL.Image as Img
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cv2

def cvread(src):
    """
    read a image with cv2, I have to say the change in plt.imread is not that good...
    Args:
        src: the path of the image
    returns:
        np.ndarray, the image in 3-channel RGB format
    """
    img = cv2.imread("/Users/alexli/Desktop/plant_book_mask.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def unique_color(img):
    """
    get all the unique colors in a np.ndarray
    Args:
        img: 3D np.ndarray, the image
    Returns:
        np.ndarray, an array including all the individual colors
    """
    return np.unique(img.reshape(-1, img.shape[2]), axis=0)

def crop_image(img):
    """
    crop all the 0 paddings aside
    input:
      img: np.ndarray, image to be cropped
    return:
      img: np.ndarray, image cropped
    """
    _x = np.nonzero(np.any(img, axis = (0,2)))[0]
    _y = np.nonzero(np.any(img, axis = (1,2)))[0]
    _xs,_xf = _x[0],_x[-1]
    _ys,_yf = _y[0],_y[-1]
    return img[_ys:_yf,_xs:_xf]

def visualize_mask(img, mask, dictionary):
    """
    A visualization of multi-class segmentation mask generated
    Discrete legend part credit to
    https://stackoverflow.com/questions/40662475/matplot-imshow-add-label-to-each-color-and-put-them-in-legend/40666123#40666123
    input:
      image, mask, dictionary, the output of image generator's .generate() function, mask is the pixel mask
    """
    _f, _axarr = plt.subplots(1,2)
    _axarr[0].set_axis_off()
    _im1 = _axarr[0].imshow(img)
    _axarr[1].set_axis_off()
    _mask = mask if mask.ndim == 2 else mask[:,:,0]
    _values = np.unique(_mask.ravel())
    _im2 = _axarr[1].imshow(_mask)
    # get the colors of the values, according to the colormap used by imshow
    _colors = [_im2.cmap(_im2.norm(value)) for value in _values]
    # create a patch (proxy artist) for every color
    _labels = ["background"] + [i for i in dictionary if dictionary[i] in values]
    _patches = [mpatches.Patch(color=_colors[i], label=_labels[i]) for i in range(len(_values))]
    # put those patched as legend-handles into the legend
    plt.legend(handles=_patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0 )
    plt.show()
    print(dictionary)

def extract_binary_mask(mask, dictionary):
    """
    convert a integer mask to multi-channel binary mask
    arg:
        mask, dictionary: output of col_gen.generate() method
    return:
        np.ndarray, the binary mask in different channel
    """
    return np.stack([np.where(mask == i, 1, 0)for i in list(dictionary.values())], axis=-1)

def unify_image_format(img, output_format: str = "np"):
    """
    convert any image input into RGB np.ndarray type
    Args:
        img:
          string, the path of image/np.ndarray/PIL.Image object, the image object
        output_format: string, "np" or "PIL", see return
    Return:
        output:
          if output_format = "np", return RGB np.ndarray,
          if output_format = "PIL", return PIL image object
    """
    assert output_format in ["np", "PIL"]
    # if it's a string
    if type(img) == str:
        output = np.array(Img.open(img).convert("RGB"))
    # if it's a np.ndarray
    elif type(img) == np.ndarray:
        # if it's the correct format
        if img.shape[2] == 3:
            output = img
        # if it's RGBA
        else:
            output = np.array(Img.fromarray(img).convert("RGB"))
    # if it's a PIL
    elif type(img) == PIL.PngImagePlugin.PngImageFile:
        output = np.array(extract_image.convert("RGB"))
    else:
        raise TypeError("Invalid image input")

    if output_format == "PIL":
        output = Img.fromarray(output)

    return output
