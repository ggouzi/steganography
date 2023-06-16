# #!/usr/bin/python

import sys
import os.path
import hashlib
from random import randrange
from PIL import Image
from argparse import ArgumentParser

parser = ArgumentParser(conflict_handler="resolve",add_help=False)
parser.add_argument("-e", "--encode", dest="encode", help="Encode message")
parser.add_argument("-d", "--decode", dest="decode", help="Decode message")
parser.add_argument("-i", "--input", dest="input", help="Name of input image file to use to encode data")
parser.add_argument("-m", "--message", dest="message", help="Plain text message")
parser.add_argument("-o", "--output", dest="output", help="Name of output image file (BMP format)")
parser.add_argument("-f", "--file", dest="file", help="Input file to encode if used with --encode (-e). Output file to store decoded output if used with --decode (-d)")
parser.add_argument("-k", "--key", dest="key", help="Plain text key used to encrypt/decrypt message. Addition of a security layer")
parser.add_argument("-g", "--generate", dest="generate", help="Generate a n x m random image")
parser.add_argument("-h", "--help", dest="help", action='store_true', help="Usage")

args = parser.parse_args()

# Usage
def usage():
    print ("Usage:")
    print("-e, --encode: Encode a message")
    print("-d, --decode: Decode a message")
    print("-i, --input: Name of input image file to use to encode data")
    print("-m, --message: Plain text message. Cannot be used with -f (--file)")
    print("-o, --output: Name of output image file (BMP format)")
    print("-f, --file: Input file to encode if used with --encode (-e), cannot be used with -f (--file). Output file to store decoded output if used with --decode (-d)")
    print("-k, --key: Plain text key used to encrypt/decrypt message. Addition of a security layer")
    print("-g, --generate: Generate a n x m random image. Can only be used alone or with -o (--output)")
    print("-h, --help: Usage")

    print("\nExamples:")
    print("Encode a plain text message:\t\t\tpython steganography.py -e myPicture.jpg -o encryptedPicture.bmp -m \"my message\"")
    print("Decode an image:\t\t\t\tpython steganography.py -d encryptedPicture.bmp -i myPicture.jpg")
    print("Encode the content of a file:\t\t\tpython steganography.py -e myPicture.jpg -o encryptedPicture.bmp -f /var/myFile.txt")
    print("Encode a plain text message with a key:\t\tpython steganography.py -e myPicture.jpg -o encryptedPicture.bmp -k mykey")
    print("Decode an image with a key:\t\t\tpython steganography.py -d encryptedPicture.bmp -i myPicture.jpg -k mykey")
    print("Generate a random image:\t\t\tpython steganography.py -g 1000x1000 -o myRandomPicture.bmp")

# Utils

def decode_binary_string(s):
    return ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8))

def hash_str(s):
    hash_object = hashlib.sha512(s.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return str(hex_dig)

def toBinary(string):
    return "".join([format(ord(char),'#010b')[2:] for char in string])

def xor_strings(data, key):
    output = ""
    for i, character in enumerate(data):
        output += chr(ord(character) ^ ord(key[i % len(key)]))
    return output

# File utils

def ReadFile(filename):
    with open(filename) as f:
        return f.read()

def writeFile(filename,data):
    with open(filename, "w") as text_file:
        print(data, file=text_file)

def dieIfFileNotFound(filename):
    if not os.path.exists(filename):
        print("File "+filename+ " not found")
        sys.exit(1)

def dieIfFileFound(filename):
    if os.path.exists(filename):
        print("File "+filename+ " already exists")
        sys.exit(1)

# Output utils

def renameOutputIfNeeded(output):
    if output.rpartition(".")[-1] != "bmp":
        output = output + ".bmp"
        print("Output file extension added: " + output)
    return output

def generateOutputImage(h, w, data):
    output = Image.new(h,w)
    output.putdata(data)
    return output

# Encoding
def encode(message, image, key):
    pixels = []
    length = image.size[0]
    width = image.size[1]
    nbPixels = length*width
    nbBits = 3*255*nbPixels

    if key is not None:
        # Hash the key to avoid guessing with many attempts and sligly changes
        key = hash_str(key)
        message = xor_strings(message, key)

    binaryMessage = toBinary(message)
    binaryMessage = [int(c)*2-1 for c in binaryMessage]

    if len(binaryMessage) > nbBits:
        print("Cannot encode " + str(len(binaryMessage)) + " bits in " + str(nbPixels) + " pixels. Reduce input message or increase image size")
        print("Number of pixels in image: " + str(nbPixels))
        print("Number of bits in image: " + str(nbBits))
        print("Number of bits in message: " + str(len(binaryMessage)))
        sys.exit(1)

    paddedMessage = [(0,0,0)]*nbPixels

    for i in range(0,len(binaryMessage),3):
        index = int(i/3)
        val0 = i
        val1 = i+1
        val2 = i+2
        if i>=len(binaryMessage)-3:
            val1 = 0
        if i>=len(binaryMessage)-2:
            val2 = 0
        paddedMessage[index] = (binaryMessage[val0],binaryMessage[val1],binaryMessage[val2])

    for y in range(0,width):
        for x in range(0,length):
            value = image.getpixel((x,y))
            index = y*width+x
            newValue = (value[0]+paddedMessage[index][0],value[1]+paddedMessage[index][1],value[2]+paddedMessage[index][2])
            pixels.append(newValue)
    return generateOutputImage('RGB', image.size, pixels)

# Decoding
def decode(image, original, key):
    lengthOrig = original.size[0]
    widthOrig = original.size[1]

    length = image.size[0]
    width = image.size[1]

    if length != lengthOrig and width != widthOrig:
        print("Error: Images are not the same size")
        sys.exit(1)

    binaryMessageArray = []
    for y in range(0,width):
        for x in range(0,length):
            valueOrig = original.getpixel((x,y))
            value = image.getpixel((x,y))
            # Skip processing uneccesary pixels
            if value[0]-valueOrig[0] == 0 or value[1]-valueOrig[1] == 0 or value[2]-valueOrig[2] == 0:
                break
            binaryMessageArray.append(value[0]-valueOrig[0])
            binaryMessageArray.append(value[1]-valueOrig[1])
            binaryMessageArray.append(value[2]-valueOrig[2])
        else:
            continue  # only executed if the inner loop did NOT break
        break  # only executed if the inner loop DID break

    binaryMessageArray[:]=[str(int((i+1)/2)) for i in binaryMessageArray]
    decoded = decode_binary_string(''.join(binaryMessageArray))

    if key is not None:
        key = hash_str(key)
        decoded = xor_strings(decoded, key)

    return decoded

# Main: Args parsing
if args.help:
    usage()

elif args.encode is not None and args.decode is None and args.generate is None:
    if not args.output:
        print("--output (-o) parameter is mandatory when encoding. Please select image output filename")
        sys.exit(1)

    dieIfFileNotFound(args.encode)
    outputFile = renameOutputIfNeeded(args.output)
    dieIfFileFound(outputFile)

    img = Image.open(args.encode)
    if args.message is None and args.file is None:
        print ("Error. Input needed. Use --message (-m) or --file (-f)")
        sys.exit(1)
    elif args.message is not None and args.file is None:
        outputImage = encode(args.message, img, args.key)
    elif args.message is None and args.file is not None:
        dieIfFileNotFound(args.file)
        message = ReadFile(args.file)
        outputImage = encode(message, img, args.key)
    else:
        print("Either --message (-m) or --file (-f) should be provided")
        sys.exit(1)

    outputImage.save(outputFile)

elif args.decode is not None and args.encode is None and args.generate is None:
    if not args.input:
        print("--input (-i) parameter is mandatory when encoding. Please select image input to compare with")
        sys.exit(1)
    dieIfFileNotFound(args.decode)
    dieIfFileNotFound(args.input)

    img = Image.open(args.decode)
    original = Image.open(args.input)
    decryptedMessage = decode(img, original, args.key)

    if args.file is not None:
        dieIfFileFound(args.file)
        writeFile(args.file, decryptedMessage)
        print("Decrypted message stored in " + args.file)
    else:
        print(decryptedMessage)

elif args.decode is None and args.encode is None and args.generate is not None:
    width, height, size = None, None, None
    try:
        size = args.generate.split('x')
        width = int(size[0])
        height = int(size[1])
    except:
        print("Cannot parse " + args.generate + " as a format. Ex: --generate 1920x1080")
        sys.exit(1)

    if not args.output:
        print("--output (-o) parameter is mandatory when encoding. Please select image output filename")
        sys.exit(1)

    outputFile = renameOutputIfNeeded(args.output)
    dieIfFileFound(outputFile)

    pixels = []
    for y in range(0,width):
        for x in range(0,height):
            pixels.append( (randrange(255),randrange(255),randrange(255)) )
    outputImage = generateOutputImage('RGB', [width,height], pixels)
    outputImage.save(outputFile)
    print("Random image " + outputFile + " of " + args.generate + " has been created")

else:
    print ("Usage: --encode (-e) OR --decode (-d) option is mandatory. Use --help (-h) to display manual")

sys.exit(0)
