from PIL import Image, UnidentifiedImageError, ImageDraw, ImageFont, ImageOps
import io
from enum import Enum
import logging as LOGGER

VAlign = Enum("VAlign",["TOP","CENTER","BOTTOM"])
HAlign = Enum("HAlign",["LEFT","CENTER","RIGHT"])
RMode = Enum("RMode",["SHRINK","ZOOM"]) # resize mode

def ar(size : tuple[int, int]) -> float:
    return size[0]/size[1]

def imgSizeCalc(imgSize : tuple[int, int], frameSize : tuple[int, int], rMode : RMode):
     # Determine new dimensions and position for the image
    frameAR = ar(frameSize)
    imgAR  = ar(imgSize)
    if (imgAR > frameAR and rMode == RMode.SHRINK) or (imgAR < frameAR and rMode == RMode.ZOOM) :
        # Image is wider relative to the target
        newImgSize = frameSize[0], frameSize[0] * imgSize[1] // imgSize[0]
    else:
        # Image is taller relative to the target
        newImgSize = int(frameSize[1] * imgSize[0] / imgSize[1]), frameSize[1]
    return newImgSize

def resizeCenterCalc(imgSize : tuple[int, int], frameSize : tuple[int, int], rMode : RMode):
    # Calculate the image size
    newSize = imgSizeCalc(imgSize, frameSize, rMode)
    # Calculate position to paste the resized image onto the new image
    pos = (frameSize[0] - newSize[0]) // 2, (frameSize[1] - newSize[1]) // 2
    return newSize, pos

def resize_and_centerImg(img : Image.Image, frameSize : tuple[int,int], backcolor : str="black", rMode : RMode = RMode.SHRINK) -> Image.Image:
    if not img: return None
    new_img : Image.Image = None
    # Calculate the image
    size, pos = resizeCenterCalc(imgSize=img.size, frameSize=frameSize, rMode=rMode)
    # Resize the image with the new dimensions while maintaining aspect ratio
    resized_img = img.resize(size)

    # Create a new image with the target size and white background
    new_img = Image.new('RGB', frameSize, backcolor)
    new_img.crop((0,0,*tuple(frameSize)))

    # Paste the resized image onto the new image
    new_img.paste(resized_img, pos)
    return new_img

   
def bytes2img(file) -> Image.Image:
    """file is filename or bytes or readbuffer (Python 3.9 on Pi can't process '|')"""
    try:
        # Open the image
        img=Image.open(file)
        return img
    except UnidentifiedImageError as e:
        LOGGER.error(f"Unidentified Image ({e})")

def imgToBytes(img : Image.Image) -> bytes:
    """Save the final image in format rteadable for frame"""
    if img:
        b=io.BytesIO()
        img.save(b, "JPEG", quality=94)
        return b.getbuffer()

def exifTranspose(img : Image.Image) -> Image.Image:
    """rotates image according to EXIF data"""
    return ImageOps.exif_transpose(img)
        


def resize_and_center(file,targetSize : tuple[int,int],**kwargs) -> Image.Image:
    """file is filename or bytes or readbuffer (Python 3.9 on Pi can't process '|')"""
    img : Image.Image = bytes2img(file)
    return resize_and_centerImg(img,targetSize=targetSize, **kwargs)

def calcAlign(align : tuple[HAlign, VAlign], size : tuple[int,int], textSize : tuple[int,int], offset : tuple[int,int]= (0,0)) -> tuple[int,int]:
        horizontal = 0
        vertical = 0
        if align[0]==HAlign.LEFT:
            horizontal = offset[0] 
        elif align[0]==HAlign.CENTER:
            horizontal = (size[0] - textSize[0]) / 2
        elif align[0]==HAlign.RIGHT:
            horizontal = size[0] - textSize[0] - offset[0] 
        if align[1]==VAlign.TOP:
            vertical = offset[1]
        elif align[1]==VAlign.CENTER:
            vertical = (size[1] - textSize[1]) / 2 
        elif align[1]==VAlign.BOTTOM:
            vertical = size[1] - textSize[1] - offset[1]
        return horizontal,vertical

def pasteImage(bgImage : Image, fgImage : Image) -> Image:
    if bgImage and fgImage:
        img : Image = bgImage.convert("RGBA")
        img.paste(fgImage, mask=fgImage)
        return img.convert("RGB")
    elif bgImage:
        return bgImage
    elif fgImage:
        return fgImage
    
def createFont(fontSize : int, fontPath : str = None) -> ImageFont:
    if fontPath:
        LOGGER.debug(f"Creating font {fontPath} {fontSize}")
        font = ImageFont.truetype(fontPath, size=fontSize)
    else:        
        font = ImageFont.load_default(fontSize)
        LOGGER.debug(f"Default font loaded {fontSize}")
    LOGGER.debug(f"Font: {font.getname()} size:{font.size}")
    return font

def drawText(text : str, size : tuple[int,int], fontSize : int, textColor, align : tuple[HAlign, VAlign], bgImage : Image, offset : tuple[int,int]=(0,0), fontPath : str = None):
        image = Image.new('RGBA', size , (0,0,0,0))
        # Initialize the drawing context
        draw = ImageDraw.Draw(image)
        font = createFont( fontSize=fontSize, fontPath=fontPath)
        textBox = draw.textbbox((0, 0), text, font=font)
        textSize : tuple[int, int] = textBox[2] - textBox[0], textBox[3] #- textBox[1]
        
        textPos : tuple[int, int] = calcAlign(align, size, textSize, offset)
        # Add text to image
        draw.text(xy=textPos,text=text,fill=textColor, font=font)
        return pasteImage(bgImage, image)
        
