#!/usr/bin/env python
 
import codecs
import os
from jinja2 import Environment, FileSystemLoader
 
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=True,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
)
OUTFILE = os.path.join(PATH, 'index.html')
 
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
 
 
def create_index_html():
    template = TEMPLATE_ENVIRONMENT.get_template('index.html')
    context = {}
    output = template.render(context)
    with codecs.open(OUTFILE, 'w', 'utf8') as f:
        f.write(output)
 
 
def main():
    create_index_html()
 
########################################
 
if __name__ == "__main__":
    main()
