from PIL import Image, ImageDraw, ImageFont
import boto3
from pprint import pprint, pformat
from io import BytesIO
import image_helpers


# --------------------------------------------------------------------
# DO NOT CHANGE THESE FUNCTIONS


def format_text(text, columns):
    '''
    Returns a copy of text that will not span more than the specified number of columns
    :param text: the text
    :param columns: the maximum number of columns
    :return: the formatted text
    '''
    # format the text to fit the specified columns
    import re
    text = re.sub('[()\']', '', pformat(text, width=columns))
    text = re.sub('\n ', '\n', text)
    return text


def text_rect_size(text, font, draw=None):
    """
    Returns the size of the rectangle to be used to
    draw as the background for the text
    :param text: the text to be displayed
    :param font: the font to be used
    :param draw: an ImageDraw.Draw object
    :return: the size of the rectangle to be used to draw as the background for the text
    """
    if draw is None:
        dummy_img = Image.new('RGB', (0, 0), (255, 255, 255, 0))
        draw = ImageDraw.Draw(dummy_img)
        (width, height) = draw.multiline_textsize(text, font=font)
        del draw
    else:
        (width, height) = draw.multiline_textsize(text, font=font)
    return (width * 1.1, height * 1.3)


def add_text_to_img(img, text, pos=(0, 0), color=(0, 0, 0), bgcolor=(255, 255, 255, 128),
                    columns=60,
                    font=ImageFont.truetype('ariblk.ttf', 22)):
    '''
    Creates and returns a copy of the image with the specified text displayed on it
    :param img: the (Pillow) image
    :param text: the text to display
    :param pos: a 2 tuple containing the xpos, and ypos of the text
    :param color: the fill color of the text
    :param bgcolor: the background color of the box behind the text
    :param columns: the max number of columns for the text
    :param font: the font to use
    :return: a copy of the image with the specified text displayed on it
    '''

    # make a blank image for the text, initialized to transparent text color
    txt_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_img)

    # format the text
    text = format_text(text, columns)
    # get the size of the text drawn in the specified font
    (text_width, text_height) = ImageDraw.Draw(img).multiline_textsize(text, font=font)

    # compute positions and box size
    (xpos, ypos) = pos
    rwidth = text_width * 1.1
    rheight = text_height * 1.4
    text_xpos = xpos + (rwidth - text_width) / 2
    text_ypos = ypos + (rheight - text_height) / 2

    # draw the rectangle (slightly larger) than the text
    draw.rectangle([xpos, ypos, xpos + rwidth, ypos + rheight], fill=bgcolor)

    # draw the text on top of the rectangle
    draw.multiline_text((text_xpos, text_ypos), text, font=font, fill=color)

    del draw  # clean up the ImageDraw object
    return Image.alpha_composite(img.convert('RGBA'), txt_img)


def get_pillow_img(imgbytes):
    """
    Creates and returns a Pillow image from the given image bytes
    :param imgbytes: the bytes of the image
    """
    return Image.open(BytesIO(imgbytes))


# NOTE: YOU DON'T NEED TO USE THIS (round_conf) FUNCTION,
#       IT IS ONLY USED BY THE DOCTESTS!
def round_conf(conf):
    """
    NOTE: YOU DON'T NEED TO USE THIS FUNCTION, IT
          IS ONLY USED BY THE DOCTESTS!

    Given a dictionary with keys Name and Confidence,
    returns a new dictionary with unchanged Name and the Confidence value rounded
    :param conf: a dictionary with keys Name and Confidence
    :return: a new dictionary with unchanged Name and the Confidence value rounded
    """
    return {'Name': conf['Name'], 'Confidence': round(conf['Confidence'])}


# END DO NOT CHANGE SECTION
# --------------------------------------------------------------------

def label_image(img, confidence=50):
    '''
    Creates and returns a copy of the image, with labels from Rekognition displayed on it
    :param img: a string that is either the URL or filename for the image
    :param confidence: the confidence level (defaults to 50)

    :return: a copy of the image, with labels from Rekognition displayed on it
    '''
    # replace pass below with your implementation
    client = boto3.client('rekognition')
    imgbytes = image_helpers.get_image(img)
    pimg = get_pillow_img(imgbytes)
    rekresp = client.detect_labels(Image={'Bytes': imgbytes}, MinConfidence=50)
    label_list = []
    for label in rekresp['Labels']:
        print(label['Name'], label['Confidence'])
        label_list.append(label['Name'])
        print(label_list)

    if 'Food' in label_list:
        if 'Hot Dog' in label_list:
            img1 = add_text_to_img(pimg, "Hot Dog", pos=(0, 0), color=(0, 220, 0))
            return img1
        else:
            img1 = add_text_to_img(pimg, "Not Hot Dog", pos=(0, 0), color=(220, 0, 0))
            return img1
    else:
        img1 = add_text_to_img(pimg, "Not Food", pos=(0, 0), color=(0, 0, 220))
        return img1


if __name__ == "__main__":
    # can't use input since PyCharm's console causes problems entering URLs
    # img = input('Enter either a URL or filename for an image: ')
    #img = 'https://render.fineartamerica.com/images/rendered/default/poster/8/10/break/images/artworkimages/medium/1/pizza-slice-diane-diederich.jpg'
    img = 'https://i.kinja-img.com/gawker-media/image/upload/s--6RyJpgBM--/c_scale,f_auto,fl_progressive,q_80,w_800/tmlwln8revg44xz4f0tj.jpg'
    #img = 'https://www.syfy.com/sites/syfy/files/styles/1140x640/public/2018/03/dragon-ball-super-goku-ultra-instinct-mastered-01.jpg'
    labelled_image = label_image(img)
    labelled_image.show()
