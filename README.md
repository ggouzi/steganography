# Steganography

The aim of this script is to hide a message into an image.
It's a symetric encryption algorithm.

# Usage

```bash
# Encode a plain text message:
$ python steganography.py -e myPicture.jpg -o encryptedPicture.bmp -m "my message"

# Encode the content of a file
$ python steganography.py -e myPicture.jpg -o encryptedPicture.bmp -f /var/myFile.txt

# Decode an image:
$ python steganography.py -d encryptedPicture.bmp -i myPicture.jpg

# Encode a plain text message with a key:
$ python steganography.py -e myPicture.jpg -o encryptedPicture.bmp -k mykey

# Decode an image with a key:
$ python steganography.py -d encryptedPicture.bmp -i myPicture.jpg -k mykey

# Generate a random image:
$ python steganography.py -g 1000x1000 -o myRandomPicture.bmp
```

# Example
```bash
# Encode message (previously encrypted with mypasskey) into lena_encrypted.bmp based on lena.png
$ python steganography.py -e lena.jpg -o lena_encrypted.bmp -m "This is a message"
```

Lena.jpg (original image)

![lena.jpg](lena.jpg)

Lena.bmp (contains hidden message)

![lena.bmp](lena.bmp)

```sh
# Image is decrypted but Message is still encrypted with a passkey
$ python steganography.py -d lena.bmp -i lena.jpg
B�T�X[\�SY�UTDE���

# Passkey is needed
$ python steganography.py -d lena.bmp -i lena.jpg -k mypasskey
This is a hidden message
```

# How does it work ?
- Encode original message into binary array (ascii) and apply it as a binary mask over the original picture
- Difference is not visible to human eye
- Addition of an additional security layer with the ability to encrypt the message before encoding it in the image (--key option). Works with a simple rotating XOR cypher algorithm. Key is previously hashed (SHA-512) to avoid hard guessing using frequency analysis
- Output image format is obviously restricted to .bmp extension. No compression allowed on the output file. However, any image format is supported as input for the original image.

**Original image needs to stay private!**
Whereas the output image can be shown to anyone. Only someone having the original image (and the passkey if addition encryption was enabled) could decrypt the message.


### Notes
Changes in bitmap image representation can be spotted by countour detection algorithms if a pixel is slighly different to the others around and does not follow any gradient rule that could naturally be explained.

As a recommendation, it's better to use a random image (full of random pixels) and not a picture taken from the web or any camera.

You can generate a random image using -g (--generate option).

# Dependencies
[PIL - Image](https://pillow.readthedocs.io/en/3.1.x/reference/Image.html)
