from PIL import Image, UnidentifiedImageError, ImageDraw, ImageFont, ImageOps
import io
from enum import Enum,IntEnum
import logging as LOGGER

VAlign = Enum("VAlign",["TOP","CENTER","BOTTOM"])
HAlign = Enum("HAlign",["LEFT","CENTER","RIGHT"])
RMode = Enum("RMode",["SHRINK","ZOOM"]) # resize mode

class Dimension(IntEnum):
    WIDTH = 0
    HEIGHT = 1

def ar(size : tuple[int, int]) -> float:
    return size[Dimension.WIDTH]/size[Dimension.HEIGHT]

def imgSizeCalc(imgSize : tuple[int, int], frameSize : tuple[int, int], rMode : RMode) -> tuple[int, int]:
     # Determine new dimensions and position for the image
    frameAR = ar(frameSize)
    imgAR  = ar(imgSize)
    if (imgAR > frameAR and rMode == RMode.SHRINK) or (imgAR < frameAR and rMode == RMode.ZOOM) :
        # Image is wider relative to the target
        newImgSize = frameSize[Dimension.WIDTH], frameSize[Dimension.WIDTH] * imgSize[Dimension.HEIGHT] // imgSize[Dimension.WIDTH]
    else:
        # Image is taller relative to the target
        newImgSize = int(frameSize[Dimension.HEIGHT] * imgSize[Dimension.WIDTH] / imgSize[Dimension.HEIGHT]), frameSize[Dimension.HEIGHT]
    return newImgSize

def imgPosCalc(imgSize : tuple[int, int], frameSize : tuple[int, int]) ->tuple[int, int]:
    """centers the image"""
    pos = (frameSize[Dimension.WIDTH] - imgSize[Dimension.WIDTH]) // 2, (frameSize[Dimension.HEIGHT] - imgSize[Dimension.HEIGHT]) // 2
    return pos

def resizeCenterCalc(imgSize : tuple[int, int], frameSize : tuple[int, int], rMode : RMode) -> tuple[tuple[int, int],tuple[int, int]]:
    """resize and center the image"""
    # Calculate the image size
    newSize = imgSizeCalc(imgSize, frameSize, rMode)
    # Calculate position to paste the resized image onto the new image
    pos = imgPosCalc(newSize, frameSize)
    return newSize, pos

def pasteImageFrame(img : Image.Image, size : tuple[int,int],pos : tuple[int,int], frameSize : tuple[int,int], backcolor : str="black") -> Image.Image:
    resized_img = img.resize(size)
    # Create a new image with the target size and black background
    new_img = Image.new('RGB', frameSize, backcolor)
    new_img.crop((0,0,*tuple(frameSize)))
    # Paste the resized image onto the new image
    new_img.paste(resized_img, pos)
    return new_img

def resize_and_centerImg(img : Image.Image, frameSize : tuple[int,int], backcolor : str="black", rMode : RMode = RMode.SHRINK) -> Image.Image:
    
    # Calculate the image
    size, pos = resizeCenterCalc(imgSize=img.size, frameSize=frameSize, rMode=rMode)
    # Resize the image with the new dimensions while maintaining aspect ratio
    return pasteImageFrame(img, size, pos, frameSize, backcolor)
   
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
    return resize_and_centerImg(img,frameSize=targetSize, **kwargs)

def calcAlign(align : tuple[HAlign, VAlign], size : tuple[int,int], textSize : tuple[int,int], offset : tuple[int,int]= (0,0)) -> tuple[int,int]:
        horizontal = 0
        vertical = 0
        if align[Dimension.WIDTH]==HAlign.LEFT:
            horizontal = offset[Dimension.WIDTH] 
        elif align[Dimension.WIDTH]==HAlign.CENTER:
            horizontal = (size[Dimension.WIDTH] - textSize[Dimension.WIDTH]) / 2
        elif align[Dimension.WIDTH]==HAlign.RIGHT:
            horizontal = size[Dimension.WIDTH] - textSize[Dimension.WIDTH] - offset[Dimension.WIDTH] 
        if align[Dimension.HEIGHT]==VAlign.TOP:
            vertical = offset[Dimension.HEIGHT]
        elif align[Dimension.HEIGHT]==VAlign.CENTER:
            vertical = (size[Dimension.HEIGHT] - textSize[Dimension.HEIGHT]) / 2 
        elif align[Dimension.HEIGHT]==VAlign.BOTTOM:
            vertical = size[Dimension.HEIGHT] - textSize[Dimension.HEIGHT] - offset[Dimension.HEIGHT]
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
        textSize : tuple[int, int] = textBox[2] - textBox[Dimension.WIDTH], textBox[3] #- textBox[Dimension.HEIGHT]
        
        textPos : tuple[int, int] = calcAlign(align, size, textSize, offset)
        # Add text to image
        draw.text(xy=textPos,text=text,fill=textColor, font=font)
        return pasteImage(bgImage, image)
        
