import os
from os import listdir
from os.path import exists
from glob import glob

try:
    import Image
except ImportError:
    from PIL import Image

import pytesseract

from consts import base_dir


def get_average_color((x, y), n, image, width, height):
    """ Returns a 3-tuple containing the RGB value of the average color of the
    given square bounded area of length = n whose origin (top left corner)
    is (x, y) in the given image"""
    if x < 0:
        x = 0
    if (x+n) >= width:
        x = width-n-1
        #print 'CORRECTED:', x

    #print x+n >= width, x+n, width, n
    if y < 0:
        y = 0
    if (y+n) >= height:
        y = height-n-1
        #print 'CORRECTED Y:', y

    r, g, b = 0, 0, 0
    count = 0
    for s in range(x, x + n + 1):
        for t in range(y, y + n + 1):
            #print s, t, width, height, n

            pixlr, pixlg, pixlb = image[s, t]
            r += pixlr
            g += pixlg
            b += pixlb
            count += 1
    return ((r / count), (g / count), (b / count))


def threshold_bw(img):
    gray = img.convert('L')
    bw = gray.point(lambda x: 0 if x < 170 else 255, '1')
    #bw.show()
    return bw

    #source = img.split()
    #mask = source[2].point(lambda i: i < 100 and 255)
    #im = Image.merge(im.mode, source)
    #

    '''
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            pix = pixels[x, y]
            #print x, y
            avg_pix = get_average_color((x-2, y-2), 4, pixels, img.width, img.height)

            # Ignore coloured text
            all_or_nothing = lambda i: (0, 0, 0) if ((sum(i) / 3) < 190) else (255, 255, 255)

            pixels[x, y] = all_or_nothing(pix)


            pixels[x, y] = (
                (255, 255, 255)
                if (
                    (abs(avg_pix[0]-avg_pix[1]) > 5) or
                    (abs(avg_pix[0]-avg_pix[2]) > 5) or
                    (abs(avg_pix[1]-avg_pix[2]) > 5)
                )
                else all_or_nothing(pix)
            )


    img = img.convert('L')
    img.show()
    return img
    '''


def process_textbook(name):
    image_dir = '%s/%s/png' % (base_dir, name.replace('_', ' '))
    image_out_dir = '%s/%s/png_out' % (base_dir, name.replace('_', ' '))
    tsv_dir = '%s/%s/tsv' % (base_dir, name.replace('_', ' '))

    for image in glob('%s/*.png' % image_dir):
        print image

        tsv_path = '%s/%s.tsv' % (tsv_dir, image.split('.')[0].split('/')[-1])
        if exists(tsv_path) and True:
            continue

        with open(tsv_path, 'wb') as f:
            img = Image.open(image)
            img = img.rotate(180)

            if img.width > 3000:
                img = img.crop((850, 950, img.width, img.height))
            else:
                img = img.crop((850/2, 950/2, img.width, img.height))

            img = img.resize((1920/2, 2715/2))
            img.save('%s/%s' % (image_out_dir, image.split('/')[-1]))
            img = threshold_bw(img)

            tsv_data = (
                pytesseract.image_to_data(img, lang='chi_sim')
            )
            f.write(tsv_data.encode('utf-8'))


if __name__ == '__main__':
    #process_textbook('10 level chinese 7 intensive')
    process_textbook('10 level chinese 7 extensive')


