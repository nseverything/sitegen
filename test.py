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
GENERIC = "generic.html"
CONTACT = "contact.html"
HEADER = "header.html"
CONTACT_DIR = "_contact"

def output_dir_exists(root_dir):
    output = os.path.join(root_dir, OUTPUT_DIR)
    if os.path.exists(output) and os.path.isdir(output):
        return True
    return False

def copy(from_path, to_path):
    copy_tree(from_path, to_path)

def copy_assets(root_dir):
    assets = os.path.join(root_dir, ASSETS)
    output = os.path.join(root_dir, OUTPUT_DIR)
    copy(assets, output)

def copy_data(output_images, item, item_images):
    output_item = os.path.join(output_images, item)
    copy(item_images, output_item)

def image_path(folder, image):
    return os.sep.join([IMAGES, folder, image])

def read_file(path, mode='r'):
    with open(path, mode) as f:
        return "\n".join(f.readlines())

def create_lists(item, item_images, item_texts):
    images = []
    for idx, item_image in enumerate(os.listdir(item_images)):
        if idx > 0:
            images.append(image_path(item, item_image))
        else:
            images.append(item_image)

    texts = []
    for item_text in os.listdir(item_texts):
        if not item_text.startswith("."):
            texts.append(os.path.join(item_texts, item_text))

    images.sort()
    texts.sort()

    return images[1:], texts, images[0]

def create_path(root_dir):
    contents_dir = os.path.join(root_dir, CONTENT)
    output_dir = os.path.join(root_dir, OUTPUT_DIR)
    return contents_dir, output_dir

def create_item_path(item_path):
    item_images = os.path.join(item_path, IMAGES)
    item_texts = os.path.join(item_path, TEXT)
    return item_images, item_texts

def generate_generic_page(filename, template, data, menu_data):
    with open(filename, "w") as f:
        f.write(
            template.render(
                payload = data,
                menu = menu_data,
            ).encode( "utf-8" )
        )

def generate_default_page(root_dir, name, template, menu_data):
    output_dir = os.path.join(root_dir, OUTPUT_DIR)
    filename = os.path.join(output_dir, name)
    with open(filename, "w") as f:
        f.write(
            template.render(
                menu = menu_data,
            ).encode( "utf-8" )
        )

def generate_contact_page(root_dir, name, template, menu_data, cont_data):
    output_dir = os.path.join(root_dir, OUTPUT_DIR)
    filename = os.path.join(output_dir, name)
    with open(filename, "w") as f:
        f.write(
            template.render(
                contacts = cont_data,
                menu = menu_data,
            ).encode( "utf-8" )
        )

def create_menu(items):
    menu = {}
    for item in items:
        menu[".".join([item, HTML])] = item.capitalize()

    return menu

def create_data(images, texts, sizes):
    data = {}
    for image, text, size in zip(images, texts, sizes):
        data[image] = [read_file(text), size]
    return data

def create_html(root_dir, name):
    output_dir = os.path.join(root_dir, OUTPUT_DIR)
    return os.path.join(output_dir, name)

def clear_output(root_dir):
    output_dir = os.path.join(root_dir, OUTPUT_DIR)
    rmtree(output_dir)

def filter(item):
    if item.startswith(".") or item.startswith("_"):
        return False
    return True

def get_dimens(item):
    w, h = item.split("x")
    return [w.strip(), h.strip()]

def prepare_size(item):
    return get_dimens(item.split(":")[1])

def create_dimens(size, item_path):
    filename = os.path.join(item_path, size)
    with open(filename, 'r') as f:
        data = f.readlines()
        data.sort()
        return [prepare_size(i) for i in data]

def read_content(root_dir, env, template):
    contents_dir, output_dir = create_path(root_dir)
    output_images = os.path.join(output_dir, IMAGES)
    items = [x for x in os.listdir(contents_dir) if filter(x)]
    menu = create_menu(items)

    for item in items:
        item_path = os.path.join(contents_dir, item)
        item_images, item_texts = create_item_path(item_path)
        images, texts, size = create_lists(item, item_images, item_texts)
        sizes = create_dimens(size, item_images)
        data = create_data(images, texts, sizes)

        # create name
        name = ".".join([item, HTML])

        # generate single page
        print("Genereting {} ".format(name))
        generate_generic_page(create_html(root_dir, name), template, data, menu)
        print("Generating {} done...".format(name))

        # copy single item data
        print("Coping assets for {}".format(name))
        copy_data(output_images, item, item_images)
        print("Coping assets for {} done...".format(name))

def default_generator(root_dir, template, item):
    print("Genereting {} ".format(item))
    contents_dir = os.path.join(root_dir, CONTENT)
    items = [x for x in os.listdir(contents_dir) if filter(x)]
    menu = create_menu(items)
    generate_default_page(root_dir, item, template, menu)
    print("Genereting {} done...".format(item))

def contact_generator(root_dir, template, item):
    print("Genereting {} ".format(item))
    contents_dir = os.path.join(root_dir, CONTENT)
    items = [x for x in os.listdir(contents_dir) if filter(x)]
    menu = create_menu(items)

    content = []
    contacts = os.path.join(contents_dir, CONTACT_DIR)
    for contact in os.listdir(contacts):
        if not contact.startswith("."):
            filename = os.path.join(contacts, contact)
            with open(filename, "r") as f:
                content.append(f.read())

    generate_contact_page(root_dir, item, template, menu, content)
    print("Genereting {} done...".format(item))

def read_templates(templates_dir, env, root_dir):
    basic = [x for x in os.listdir(templates_dir) if not x.startswith(".")]
    for item in basic:
        if item != HEADER:
            template = env.get_template(item)

            if item == GENERIC:
                read_content(root_dir, env, template)
            elif item == CONTACT:
                contact_generator(root_dir, template, item)
            else:
                default_generator(root_dir, template, item)
        else:
            continue

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, TEMPLATES)
    env = Environment(loader = FileSystemLoader(templates_dir))

    # Test is there output dirname
    if not output_dir_exists(root):
        print("Output folder does not exits, create one...")
        output = os.path.join(root, OUTPUT_DIR)
        os.makedirs(output)

    # Clear previous content of output folder
    clear_output(root)

    # Copy general assets to output folder
    copy_assets(root)

    # Than generate all of the content
    read_templates(templates_dir, env, root)
