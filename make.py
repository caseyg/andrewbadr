#!/usr/bin/env python
 
import codecs
import os

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image

#                           Width, Height 
FEATURED_THUMBNAIL_SIZE =   (464, 348) # 'featured_thumb'
FEATURED_MAX_SIZE =         (1000, 750) # 'featured'
SMALL_IMAGE_SIZE =          (50, 50) # 'small'

STATIC_OUTPUT_DIR = '_gen_homepage_static' # This is a folder name, not a path

def here(*args):
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, *args)

# From https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
from collections import OrderedDict
def ordered_load_yaml(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

#featured_projects = [
#    'description_html': d,
#    'thumb_url': '...',
#    'image_urls': ['...',]
#]

def ratio_matches((w1, h1), (w2, h2)):
    return w1*h2 == w2*h1

def process_image(project_name, image_path, size_name):
    # TODO: make filename depend on hash so we detect changes
    outdir = here(STATIC_OUTPUT_DIR)
    _, filename = os.path.split(image_path)
    base, ext = os.path.splitext(filename)
    new_filename = "%s_%s_%s%s" % (project_name, base, size_name, ext.lower())
    new_filepath = os.path.join(outdir, new_filename)
    if os.path.exists(new_filepath):
        print "Existing", new_filepath, "..."
        width, height = Image.open(new_filepath).size
    else:
        print "Writing", new_filepath, "..."
        im = Image.open(image_path)
        size = {
            'featured_thumb': FEATURED_THUMBNAIL_SIZE,
            'featured': FEATURED_MAX_SIZE,
            'small': SMALL_IMAGE_SIZE,
        }[size_name]
        if size_name in ('featured_thumb', 'small'):
            # Assert size matches
            assert ratio_matches(im.size, size)
        else:
            assert size_name == 'featured' #:>
        im.thumbnail(size, Image.ANTIALIAS)
        #im = im.convert('RGB') # RGB for JPEG
        im.save(new_filepath)
        width, height = im.size # Get final size
    url = os.path.join(STATIC_OUTPUT_DIR, new_filename)
    return url, width, height


def load_featured_project(project_name):
    md_path = here('projects', 'descriptions', project_name + '.md')
    with codecs.open(md_path, 'r', 'utf8') as f:
        description = markdown.markdown(f.read())
    image_dir = here('projects', 'images', project_name)

    # load the small 4x3 thumbnail
    thumb_path = os.path.join(image_dir, 'thumb.jpg')
    thumb_url, _, _ = process_image(project_name, thumb_path, 'featured_thumb')

    # Load all the big images
    images = []
    # This sorted() is important. We use alphabetic naming
    # to control the display order.
    for filename in sorted(os.listdir(image_dir)):
        if filename == 'thumb.jpg':
            continue
        if filename.startswith('_'):
            continue
        image_path = os.path.join(image_dir, filename)
        url, w, h = process_image(project_name, image_path, 'featured')
        images.append({
            'url': url,
            'width': w,
            'height': h
        })

    return {
        'thumb_url': thumb_url,
        'description_html': description,
        'images': images,
    }

def load_small_project(project_name, project_data):
    image_dir = here('projects', 'images', project_name)
    images = os.listdir(image_dir)
    if not images:
        image_path = './default_small.png'
    else:
        assert len(images) == 1 # exactly 1 image per small project
        image_path = os.path.join(image_dir, images[0])
    url, _, _ = process_image(project_name, image_path, 'small')
    return {
        'img_url': url,
        'text': project_data['text'],
        'link': project_data.get('url'),
    }

def load_project_data():
    featured_projects = []
    small_projects = []
    yaml_data = open(here('projects', 'projects.yaml')).read()
    data = ordered_load_yaml(yaml_data)
    for project_name in data['Featured']:
        featured_projects.append(load_featured_project(project_name))
    for project_name, project_data in data['Small'].items():
        small_projects.append(load_small_project(project_name, project_data))
    return featured_projects, small_projects

 
def create_index_html():
    loader = FileSystemLoader(here('templates'))
    env = Environment(autoescape=True, loader=loader)
    template = env.get_template('index.html')
    featured_projects, small_projects = load_project_data()
    context = {
        'featured_projects': featured_projects,
        'small_projects': small_projects
    }
    outfile = here('index.html')
    output = template.render(context)
    with codecs.open(outfile, 'w', 'utf8') as f:
        f.write(output)
 
def main():
    create_index_html()
 
########################################
 
if __name__ == "__main__":
    main()
