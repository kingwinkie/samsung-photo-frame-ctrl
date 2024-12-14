from PIL import Image, UnidentifiedImageError
import io

def resize_and_centerImg(img : Image.Image, targetSize : tuple[int,int], backcolor : str="black") -> Image.Image:
    new_img : Image.Image = None
    try:
        # Calculate the aspect ratio of the image
        img_ratio = img.width / img.height
        target_ratio = targetSize[0] / targetSize[1]

        # Determine new dimensions and position for the image
        if img_ratio > target_ratio:
            # Image is wider relative to the target
            newSize = targetSize[0], int(targetSize[0] / img_ratio)
        else:
            # Image is taller relative to the target
            newSize = int(targetSize[1] * img_ratio), targetSize[1]

        # Resize the image with the new dimensions while maintaining aspect ratio
        resized_img = img.resize(newSize)

        # Create a new image with the target size and white background
        new_img = Image.new('RGB', targetSize, backcolor)

        # Calculate position to paste the resized image onto the new image
        paste = (targetSize[0] - newSize[0]) // 2, (targetSize[1] - newSize[1]) // 2

        # Paste the resized image onto the new image
        new_img.paste(resized_img, paste)
    except UnidentifiedImageError:
        pass
    return new_img

def bytes2img(file : bytes) -> Image:
    try:
        img = Image.open(file)
        return img
    except UnidentifiedImageError:
        pass
    
def resize_and_center(file,targetSize : tuple[int,int],**kwargs) -> Image.Image:
    """file is filename or bytes or readbuffer (Python 3.9 on Pi can't process '|')"""
    new_img : Image.Image = None
    try:
        # Open the image
        with Image.open(file) as img:
            return resize_and_centerImg(img,targetSize=targetSize, **kwargs)
    except UnidentifiedImageError:
        pass
    return new_img


def imgToBytes(img : Image.Image) -> bytes:
    """Save the final image in format rteadable for frame"""
    if img:
        b=io.BytesIO()
        img.save(b, "JPEG", quality=94)
        return b.getbuffer()

