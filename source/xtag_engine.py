#!/usr/bin/python3

import yaml
import xtag_md_parse as parse



XTag = namedtuple("XTag", ["references",
                           "parsedtext",
                           "project"
                           "isrequirement"])

def get_project_name():
    #TODO - dont hardcode
    return "xtag-demo"

def write_metadata(ofile, metadata):
    with open(ofile, 'w') as yaml_file:
        yaml_file.write( yaml.dump(metadata, default_flow_style=False))

if __name__ == '__main__':

    xtags = parse.render('../examples/unmarked/marketing-requirements.md')

    write_metadata(xtags)
    #print(mydict)
