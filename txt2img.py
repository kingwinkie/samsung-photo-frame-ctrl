#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from PIL import Image, ImageDraw, ImageFont, ImageColor
import sys
import config
import logging as LOGGER
import resize
# Create a blank image with white background
def createImage(text : str, size : tuple[int,int] = config.IMG_SIZE, fontSize : int = 24,  backcolor : str = 'black', textcolor : str = 'white', fontPath : str = None) -> Image.Image:
    image = Image.new('RGBA', size, backcolor)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    if fontPath:
        font = ImageFont.truetype(fontPath, size=fontSize)
    else:
        font = ImageFont.load_default(fontSize)
    
    # Calculate the bounding box of the text to be added
    bbox = draw.textbbox((0, 0), text, font=font)
    textSize : tuple[int, int] = bbox[2] - bbox[0], bbox[3] - bbox[1]
    textPos : tuple[int, int] = (size[0] - textSize[0]) / 2, (size[1] - textSize[1]) / 2

    # Add text to image
    draw.text(textPos, text, fill=textcolor, font=font)
    return image

    
def addBgImage(img : Image.Image, bgImage : str, size = config.IMG_SIZE, backcolor : str = "black"):
    bgImg : Image.Image = resize.resize_and_center(bgImage, targetSize=size, backcolor=backcolor)
    if bgImg:
        bgImg.paste(img, mask=img)
        img = bgImg
    return img

def showImage( img : Image ):
    if img:
        # Display the image
        img.show()

def main():
    parser = argparse.ArgumentParser(exit_on_error=True,
                    prog='text2img',
                    description='This software renders image from text',
                    epilog="""
                    If there's no --input or --textinput specified the software reads from stdin.
                    If there's no --output specified the output is stdout.
                    """)

    parser.add_argument('-i','--input', help="Input text file")
    parser.add_argument('-ti','--textinput', help="Input text")
    parser.add_argument('-bi','--bgimage', help="Background image")
    parser.add_argument('-o', '--output', help="Output image file. If - stdout is used") 
    parser.add_argument('-fs', '--fontsize', help="Font size", default=24, type=int)
    parser.add_argument('-fp', '--fontpath', help="Path to TTF or OTF font")
    parser.add_argument('-pw', '--pwidth', help="Picture Width", default=config.IMG_SIZE[0], type=int)
    parser.add_argument('-ph', '--pheight', help="Picture Height", default=config.IMG_SIZE[1], type=int)
    parser.add_argument('-b', '--backcolor', help="Back color (black, white etc.)", type=ImageColor.colormap.get)
    parser.add_argument('-t', '--textcolor', help="Text color", default='white', type=ImageColor.colormap.get)
    parser.add_argument('-s', '--show', action='store_true', help="Show Image")
    parser.add_argument('-v', '--verbose', action='store_true') 
    
    args = parser.parse_args()
    logLevel : LOGGER = LOGGER.DEBUG if args.verbose else LOGGER.ERROR
    size = (int(args.pwidth),int(args.pheight))
    LOGGER.basicConfig(level=logLevel)
    LOGGER.info("Starting")
    inputText : str = ""
    if args.input:
        LOGGER.debug(f"Reading file {args.input}")
        with open( args.input, "r") as inputFile:
            inputText = inputFile.read()
    elif args.textinput:
        LOGGER.debug(f"Text: {args.textinput}")
        inputText = args.textinput
    else: #wait for stdin
        LOGGER.info(f"Waiting for stdin")
        inputText = sys.stdin.read()
    
    backcolor : str = args.backcolor if args.backcolor else 'black' #set default color
    if args.bgimage:
        backcolor = (*ImageColor.getrgb(backcolor),128) if backcolor else (0, 0, 0, 0) #half transparency if backcolor is set. Othervise full transparency

    img : Image.Image = createImage(inputText, size, args.fontsize, backcolor , args.textcolor, args.fontpath)

    if img:
        if args.bgimage:
           img = addBgImage(img, args.bgimage, size=size, backcolor=backcolor)

        if args.output:
            if args.output == '-':
                LOGGER.debug(f"Writing to stdout")
                img.save(sys.stdout, "JPG", quality=94)
            else:
                LOGGER.debug(f"Writing to {args.output}")
                img.convert(mode="RGB").save(args.output)
        if args.show:
            LOGGER.debug(f"Showing Image")
            showImage(img)
            LOGGER.info(f"Press Enter")
            input()

    LOGGER.info("End")
    

if (__name__ == "__main__"):
    main()