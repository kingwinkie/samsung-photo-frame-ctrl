from PIL import Image, ImageDraw, ImageFont
import logging as LOGGER

def drawText(text : str, size : tuple[int,int], fontSize : int, textColor, halign : str, valign : str, bkImage : Image, offset : tuple[int,int]=(0,0)):
        image = Image.new('RGBA', size , (0,0,0,0))
        # Initialize the drawing context
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(fontSize)
        bbox = draw.textbbox((0, 0), text, font=font)
        textSize : tuple[int, int] = bbox[2] - bbox[0], bbox[3] #- bbox[1]

        horizontal = 0
        vertical = 0
        if halign=="left":
            horizontal = offset[0] 
        elif halign=="right":
            horizontal = size[0] - textSize[0] - offset[0] 
        elif halign=="center":
             horizontal = (size[0] - textSize[0]) / 2
        if valign=="top":
             vertical = offset[1]
        elif valign=="bottom":
            vertical = size[1] - textSize[1] - offset[1]
        elif valign=="center":
             vertical = (size[1] - textSize[1]) / 2 

        textPos : tuple[int, int] = (horizontal, vertical)
        # Add text to image
        draw.text(xy=textPos,text=text,fill=textColor, font=font)
        if bkImage:
            img : Image = bkImage.convert("RGBA")
            img.paste(image, mask=image)
            return img.convert("RGB")