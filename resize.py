import config
from PIL import Image, UnidentifiedImageError
import io

def resize_and_centerImg(img : Image) -> Image:
    new_img : Image = None
    try:
        target_width, target_height = config.IMG_SIZE

        # Calculate the aspect ratio of the image
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        # Determine new dimensions and position for the image
        if img_ratio > target_ratio:
            # Image is wider relative to the target
            new_width = target_width
            new_height = int(new_width / img_ratio)
        else:
            # Image is taller relative to the target
            new_height = target_height
            new_width = int(new_height * img_ratio)

        # Resize the image with the new dimensions while maintaining aspect ratio
        resized_img = img.resize((new_width, new_height))

        # Create a new image with the target size and white background
        new_img = Image.new('RGB', config.IMG_SIZE, (0, 0, 0))

        # Calculate position to paste the resized image onto the new image
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2

        # Paste the resized image onto the new image
        new_img.paste(resized_img, (paste_x, paste_y))
    except UnidentifiedImageError:
        pass
    return new_img

def resize_and_center(inStream : bytes) -> Image:
    new_img : Image = None
    try:
        # Open the image
        with Image.open(inStream) as img:
            return resize_and_centerImg(img)
    except UnidentifiedImageError:
        pass
    return new_img


def imgToBytes(img : Image) -> bytes:
    """Save the final image in format rteadable for frame"""
    if img:
        b=io.BytesIO()
        img.save(b, "JPEG", quality=94)
        return b.getbuffer()

