#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from PIL import Image, ImageDraw, ImageFont
import sys
import io
import logging as LOGGER

# Create a blank image with white background
def createImage(text : str, width : int = 400, height : int = 200, fontSize : int = 24,  backcolor : str = 'black', textcolor : str = 'white', fontPath : str = None) -> Image:
    image = Image.new('RGB', (width, height), backcolor)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    if fontPath:
        font = ImageFont.truetype(fontPath, size=fontSize)
    else:
        font = ImageFont.load_default(fontSize)
    

    # Calculate the bounding box of the text to be added
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Calculate X, Y position of the text
    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # Add text to image
    draw.text((x, y), text, fill=textcolor, font=font)
    return image

    


def showImage( img : Image ):
    if img:
        # Display the image
        img.show()

def main():
    parser = argparse.ArgumentParser(
                    prog='text2img',
                    description='This software renders image from text',
                    epilog="""
                    If there's no --input or --textinput specified the software reads from stdin.
                    If there's no --output specified the output is stdout.
                    """)

    parser.add_argument('-i','--input', help="Input text file")
    parser.add_argument('-ti','--textinput', help="Input text file")
    parser.add_argument('-o', '--output', help="Output image file. If - stdout is used") 
    parser.add_argument('-fs', '--fontsize', help="Font size", default=24)
    parser.add_argument('-fp', '--fontpath', help="Path to TTF or OTF font")
    parser.add_argument('-pw', '--pwidth', help="Picture Width", default=800)
    parser.add_argument('-ph', '--pheight', help="Picture Height", default=600)
    parser.add_argument('-b', '--backcolor', help="Back color (black, white etc.)", default='black')
    parser.add_argument('-t', '--textcolor', help="Text color", default='white')
    parser.add_argument('-s', '--show', action='store_true', help="Show Image", default=False)
    parser.add_argument('-v', '--verbose', action='store_true') 
    
    args = parser.parse_args()
    logLevel : LOGGER = LOGGER.DEBUG if args.verbose else LOGGER.ERROR
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
        
    img : Image = createImage(inputText, args.pwidth, args.pheight, args.fontsize, args.backcolor, args.textcolor, args.fontpath)
    if args.output:
        if args.output == '-':
            LOGGER.debug(f"Writing to stdout")
            img.save(sys.stdout, "JPG", quality=94)
        else:
            LOGGER.debug(f"Writing to {args.output}")
            img.save(args.output)
    if args.show:
        LOGGER.debug(f"Showing Image")
        showImage(img)
        LOGGER.info(f"Press Enter")
        input()
    LOGGER.info("End")
    

if (__name__ == "__main__"):
    main()