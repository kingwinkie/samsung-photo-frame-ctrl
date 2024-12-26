#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from PIL import Image, ImageDraw, ImageFont, ImageColor
import sys
import logging as LOGGER
import imgutils as imgutils
from os import path as osp
from dynaconf import Dynaconf

myPath = osp.realpath(osp.dirname(__file__))
settings = Dynaconf(
    envvar_prefix="FRAME",

    settings_files=[osp.join(myPath,'settings.toml'), osp.join(myPath,'.secrets.toml') ]
)
# Create a blank image with white background
def createImage(text : str, size : tuple[int,int] = settings.FRAME.IMG_SIZE, fontSize : int = 24,  backcolor : str = 'black', textcolor : str = 'white', fontPath : str = None) -> Image.Image:
    image = Image.new('RGBA', size, backcolor)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    if fontPath:
        LOGGER.debug(f"Creating font {fontPath} {fontSize}")
        font = ImageFont.truetype(fontPath, size=fontSize)
        if font:
             
            LOGGER.debug(f"Font created")
    else:
        font = ImageFont.load_default(fontSize)
        if font:
            LOGGER.debug(f"Default font loaded {fontSize}")
    LOGGER.info(f"Font: {font.getname()} size:{font.size}")
    
    # Calculate the bounding box of the text to be added
    bbox = draw.textbbox((0, 0), text, font=font)
    textSize : tuple[int, int] = bbox[2] - bbox[0], bbox[3] - bbox[1]
    textPos : tuple[int, int] = (size[0] - textSize[0]) / 2, (size[1] - textSize[1]) / 2

    # Add text to image
    draw.text(textPos, text, fill=textcolor, font=font)
    return image

    
def addBgImage(img : Image.Image, bgImage : str, size = settings.FRAME.IMG_SIZE, backcolor : str = "black"):
    bgImg : Image.Image = imgutils.resize_and_center(bgImage, targetSize=size, backcolor=backcolor)
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
    parser.add_argument('-pw', '--pwidth', help="Picture Width", default=settings.FRAME.IMG_SIZE[0], type=int)
    parser.add_argument('-ph', '--pheight', help="Picture Height", default=settings.FRAME.IMG_SIZE[1], type=int)
    parser.add_argument('-bc', '--backcolor', help="Back color (black, white etc.)", type=ImageColor.colormap.get)
    parser.add_argument('-tc', '--textcolor', help="Text color", default='white', type=ImageColor.colormap.get)
    parser.add_argument('-s', '--show', action='store_true', help="Show Image")
    parser.add_argument('-v', '--verbose', help="Show Info messages", action='store_true') 
    
    args = parser.parse_args()
    logLevel : LOGGER = LOGGER.DEBUG if args.verbose else LOGGER.ERROR
    size = (int(args.pwidth),int(args.pheight))
    LOGGER.basicConfig(level=logLevel, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
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

    img : Image.Image = createImage(text=inputText, size=size, fontSize=args.fontsize, backcolor=backcolor , textcolor=args.textcolor, fontPath=args.fontpath)

    if img:
        if args.bgimage:
           img = addBgImage(img, args.bgimage, size=size, backcolor=backcolor)

        if args.output:
            if args.output == '-':
                LOGGER.debug(f"Writing to stdout")
                img.convert(mode="RGB").save(sys.stdout, "JPEG", quality=94)
            else:
                LOGGER.debug(f"Writing to {args.output}")
                img.convert(mode="RGB").save(args.output)
        if args.show:
            LOGGER.debug(f"Showing Image")
            showImage(img)
            
    LOGGER.info("End")
    

if (__name__ == "__main__"):
    
    main()