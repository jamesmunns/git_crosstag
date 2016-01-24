#!/usr/bin/python3
import markdown
import re
import hashlib
import yaml

TAG_RE = re.compile(r'<[^>]+>')

def get_project_name():
    #TODO - dont hardcode
    return "xtag-demo"

def read_file(filename):
    lines = None
    with open(filename,'r',encoding='utf-8') as ifile:
        lines = [line.rstrip() for line in ifile if line != '']
    return lines

def remove_tags(text):
    return TAG_RE.sub('', text)

def contents_to_reqs(contents):
    # TODO: Also generate implicit parent linkage, before parsing?

    reqs = []
    for line in contents:
        # Parse Markdown
        x = markdown.markdown(line)

        # Remove HTML - TODO: do we want this?
        x = remove_tags(x)

        x = x.strip()

        if x != '':
            reqs.append(x)

    return reqs

def generate_metadata(requirement):
    inputtext = get_project_name() + requirement

    # TODO: Whats up with SHA-1 and unicode encoding?
    return hashlib.sha1(inputtext.encode('utf-8')).digest().hex()

def write_metadata(ofile, metadata):
    with open(ofile, 'w') as yaml_file:
        yaml_file.write( yaml.dump(metadata, default_flow_style=False))



if __name__ == '__main__':
    contents = read_file('../examples/unmarked/marketing-requirements.md')
    reqs     = contents_to_reqs(contents)

    mydict = {}
    for req in reqs:
        mydict[generate_metadata(req)] = {'parsetext': req,
                                          'parents'  : [],
                                          'crossrefs': []}


    write_metadata('../examples/unmarked/marketing-requirements.md.xtag', mydict)
    #print(mydict)
