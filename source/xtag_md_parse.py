import markdown
import re
import hashlib

from xtag_engine import XTag, get_project_name

TAG_RE = re.compile(r'<[^>]+>')
NUMBERED_LIST_RE = re.compile(r'\d+.')

BULLET_MARKS = ['*', '-', '+']

def render(filename):
    contents = parse.read_file(filename)
    reqs     = contents_to_reqs(contents)



    return reqs

def read_file(filename):
    lines = None
    with open(filename,'r') as ifile:
        lines = [line.rstrip() for line in ifile]
    return lines

def seek_list_parent(file_line, contents):
    for line in reversed(range(file_line)):

        # Unaccptable parent(s):
        #   - blank lines
        #
        #TODO - Any other parent items to avoid?
        if contents[line].strip() == '':
            return []

        # Known matches:
        #   - regular text
        #   - parent bullet
        else:
            return [line]

def seek_line_parent(file_line, contents):
    for line in reversed(range(file_line)):

        # A header line is the only appropriate parent
        if contents[line].lstrip().startswith('#'):
            return [line]

        else:
            return []

def seek_header_parent(file_line, contents):

    def header_level(line):
        sline = line.lstrip()
        return len(sline) - len(sline.lstrip('#'))


    init = header_level(contents[file_line])

    # Header parent is any heading larger (smaller number) than current
    for line in reversed(range(file_line)):
        if header_level(contents[line]) < init:
            return [line]

    # No match
    return []


def obtain_implicit_references(file_line, contents):

    def get_switch(line):
        return line.lstrip()[0]

    switch = get_switch(contents[file_line])

    # TODO: Is multiple parents ever an option?

    # Handle bullet points
    if switch in BULLET_MARKS:
        return seek_list_parent(file_line, contents)

    # Handle numeric lists
    elif NUMBERED_LIST_RE.match(contents[file_line].lstrip()):
        return seek_list_parent(file_line, contents)

    # Handle headings - TODO Setext headers
    elif switch == '#':
        return seek_header_parent(file_line, contents)

    # default handling
    else:
        return seek_line_parent(file_line, contents)

def is_line_requirement(i, line):
    # TODO
    return True

def line_to_parsetext(inputline):
    # Parse Markdown
    x = markdown.markßdown(inputline)

    # Remove HTML - TODO: do we want this?
    x = remove_tags(inputline)

    # Remove whitespace
    x = x.strip()

    return x

def contents_to_reqs(contents):

    project = get_project_name()

    reqs = []
    for i, line in enumerate(contents):

        if line.strip() == '':
            continue

        references    = obtain_implicit_references(i, contents)
        parsedtext    = line_to_parsetext(line)
        isrequirement = is_line_requirement(i, line)

        if parsedtext != '':
            reqs.append(XTag(references=references,
                             parsedtext=parsedtext,
                             project=project,
                             isrequirement=isrequirement))

    mydict = {}
    for req in reqs:

        mydict[generate_metadata(req)] = req

    return reqs

def generate_metadata(requirement):
    inputtext = get_project_name() + requirement.parsedtext

    # TODO: Whats up with SHA-1 and unicode encoding?
    return hashlib.sha1(inputtext.encode('utf-8')).digest().hex()
