import config
from PIL import Image
import io
def resize_and_center(inStream):
    # Open the image
    with Image.open(inStream) as img:
        # Calculate the aspect ratio of the image
        img_ratio = img.width / img.height
        target_width, target_height = config.IMG_SIZE
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

        # Save the final image
        b=io.BytesIO()
        new_img.save(b,"JPEG")
        # return new_img.tobytes("jpeg","RGB")
        # new_img.save(output_path)
        return b.getbuffer()

