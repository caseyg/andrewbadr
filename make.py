#!/usr/bin/env python
 
import codecs
import os

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image

IMAGE_OUTPUT_SIZES = [
    # Width, Height
    (1000, 750),
    (465, 349),
]

SMALL_IMAGE_SIZE = (50, 50)

STATIC_OUTPUT_DIR = '_gen_homepage_static'

def here(*args):
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, *args)

#featured_projects = [
#    'description_html': d,
#    {
#        'images': [
#            {
#                'size_1000_750': {
#                    'url': 'http://placehold.it/1000x750',
#                },
#                'size_465_349': {
#                    'url': 'http://placehold.it/465x349',
#                },
#                'caption': '',
#            }
#
#        ],
#    },
#]

def process_featured_image(image_path):
    outdir = here(STATIC_OUTPUT_DIR)
    result = {'caption': ''} # captions later?
    _, filename = os.path.split(image_path)
    base, _ = os.path.splitext(filename)
    for width, height in IMAGE_OUTPUT_SIZES:
        new_filename = "%s_%d_%d.jpg" % (base, width, height)
        new_filepath = os.path.join(outdir, new_filename)
        if os.path.exists(new_filepath):
            print "Existing", new_filepath, "..."
        else:
            print "Writing", new_filepath, "..."
            im = Image.open(image_path)
            sized = im.resize((width, height)).convert('RGB') # ensure RGB for JPEG
            sized.save(new_filepath, "JPEG")
        result['size_%d_%d' % (width, height)] = {
            'url': '%s/%s' % (STATIC_OUTPUT_DIR, new_filename)
        }
    return result


def load_featured_project(project_name):
    md_path = here('projects', 'descriptions', project_name + '.md')
    with codecs.open(md_path, 'r', 'utf8') as f:
        description = markdown.markdown(f.read())
    images = []
    image_dir = here('projects', 'images', project_name)

    # This sorted() is important. We use alphabetic naming
    # to control the display order.
    for filename in sorted(os.listdir(image_dir)):
        image_path = os.path.join(image_dir, filename)
        image_data = process_featured_image(image_path)
        images.append(image_data)
    return {
        'description_html': description,
        'images': images,
    }

def load_small_project(project_name, project_data):
    image_dir = here('projects', 'images', project_name)
    images = os.listdir(image_dir)
    assert len(images) == 1 # exactly 1 image per small project
    image_path = os.path.join(image_dir, images[0])
    base, _ = os.path.splitext(images[0])
    outdir = here(STATIC_OUTPUT_DIR)
    width, height = SMALL_IMAGE_SIZE
    new_filename = "%s_%d_%d.jpg" % (base, width, height)
    new_filepath = os.path.join(outdir, new_filename)
    if os.path.exists(new_filepath):
        print "Existing", new_filepath, "..."
    else:
        print "Writing", new_filepath, "..."
        im = Image.open(image_path)
        sized = im.resize((width, height)).convert('RGB') # ensure RGB for JPEG
        sized.save(new_filepath, "JPEG")
    return {
        'img_url': '%s/%s' % (STATIC_OUTPUT_DIR, new_filename),
        'text': project_data['text'],
        'link': project_data.get('url'),
    }

def load_project_data():
    featured_projects = []
    small_projects = []
    data = yaml.load(open(here('projects', 'projects.yaml')).read())
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
    print context
    outfile = here('index.html')
    output = template.render(context)
    with codecs.open(outfile, 'w', 'utf8') as f:
        f.write(output)
 
def main():
    create_index_html()
 
########################################
 
if __name__ == "__main__":
    main()
