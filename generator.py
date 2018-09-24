from jinja2 import Environment, FileSystemLoader
import os
from distutils.dir_util import copy_tree
import ftplib
from shutil import rmtree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

TEMPLATES = "templates"
OUTPUT_DIR = "output"
CONTENT = "content"
HTML = "html"
IMAGES = "images"
TEXT = "text"
ASSETS = "assets"
FILE = "secrets.txt"

'''
Read names of the content folder that should be generated
And use that to populate menu item on the main page
'''
def load_names(content_dir):
    names = {}
    for name in os.listdir(content_dir):
        if not name.startswith("."):
            names[".".join([name, HTML])] = name.capitalize() 

    return names

'''
Read the content of the conresponding text file for
the image, that should be shown
'''
def read_text(path):
    text = ""
    with open(path, "r") as f:
        text = '\n'.join(f.readlines())

    return text

'''
Read images and text files from filder that
describe single content element or single page
'''
def read(path):
    content = []
    for cnt in os.listdir(path):
        if not cnt.startswith("."):
            content.append(cnt)
    return content


'''
Create final data, that consists of path image
as the key, and text content for that image as
a content
'''
def get_data(path):
    name = path.split(os.sep)[-1]
    os.sep.join([name, IMAGES])

    images_dir = os.path.join(path, IMAGES)
    text_dir = os.path.join(path, TEXT)

    texts = read(text_dir)
    images = read(images_dir)
    images.sort()
    texts.sort()

    data = {}
    for item in zip(images, texts):
        text_path = os.path.join(text_dir, item[1])
        image_path = os.sep.join([IMAGES, name, item[0]])
        data[image_path] = read_text(text_path)

    return data

'''
Populate data element using previous function
and name of the single content element from folder
'''
def load_data(content_dir):
    content = {}
    for part in os.listdir(content_dir):
        if not part.startswith("."):
            data = get_data(os.path.join(content_dir, part))
            content[part] = data

    return content

'''
Render single template elemen
'''
def render_template(filename, template, data, menu_data):
    with open(filename, "w") as f:
        f.write(
            template.render(
                payload = data,
                menu = menu_data,
            ).encode( "utf-8" )
        )

def render_templates(env, contents_dir, menu_data):
    map_data = load_data(contents_dir)
    for key in map_data:
        name = ".".join([key, HTML])
        template = env.get_template(name)
        filename = os.path.join(OUTPUT_DIR, name)

        render_template(filename, template, map_data[key], menu_data)
'''
Coppy all assets like css or js files to output folder
so that all is at the same place, and that is easier
to send to FTP server
'''
def copy_assets(root_dir, menu_items, contents_dir):
    assets_dir = os.path.join(root_dir, ASSETS)
    output_dir = os.path.join(root_dir, OUTPUT_DIR)

    rmtree(output_dir)
    copy_tree(assets_dir, output_dir)

    images_dir = os.path.join(output_dir, IMAGES)
    for key in menu_items:
        directory = os.path.join(images_dir, key.lower())
        if not os.path.exists(directory):
            os.makedirs(directory)
            item_path = os.path.join(contents_dir, key.lower())
            item_images = os.path.join(item_path, IMAGES)
            copy_tree(item_images, directory)

def ftp_upload(root_dir):
    with open(FILE, r) as f:
        username, password, server = f.readline().split("|")
        myFTP = ftplib.FTP(server, username, password)
        path = os.path.join(root_dir, OUTPUT_DIR)

        upload(path, myFTP)

def upload(path, myFTP):
    files = os.listdir(path)
    os.chdir(path)
    for f in files:
        if os.path.isfile(path + r'\{}'.format(f)):
            fh = open(f, 'rb')
            myFTP.storbinary('STOR %s' % f, fh)
            fh.close()
        elif os.path.isdir(path + r'\{}'.format(f)):
            myFTP.mkd(f)
            myFTP.cwd(f)
            uploadThis(path + r'\{}'.format(f))
    myFTP.cwd('..')
    os.chdir('..')

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, TEMPLATES)
    contents_dir = os.path.join(root, CONTENT)
    env = Environment( loader = FileSystemLoader(templates_dir) )

    menu_data = load_names(contents_dir)
    print("Reading menu done..,")

    copy_assets(root, menu_data.values(), contents_dir)
    print("Assets coping done...")

    render_templates(env, contents_dir, menu_data)
    print("Render done....")

    # ftp_upload(root)
    # print("FTP Upload done...")
