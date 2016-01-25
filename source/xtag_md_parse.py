import markdown
import re
import hashlib

from xtag_engine import XTag, get_project_name

TAG_RE = re.compile(r'<[^>]+>')
NUMBERED_LIST_RE = re.compile(r'\d+.')

BULLET_MARKS = ['*', '-', '+']

def remove_tags(text):
    return TAG_RE.sub('', text)

def render(filename):
    contents = read_file(filename)
    reqs     = contents_to_reqs(contents)

    xtags = {}

    for req in reqs:
        xtags[generate_metadata(req)] = req

    return xtags

def read_file(filename):
    lines = None
    with open(filename,'r') as ifile:
        lines = [line.rstrip() for line in ifile]
    return lines

def seek_list_parent(file_line, contents):

    def leading_spaces(line_in):
        return len(line_in) - len(line_in.lstrip())

    for line in reversed(range(file_line)):

        # Unaccptable parent(s):
        #   - blank lines
        #
        #TODO - Any other parent items to avoid?
        if contents[line].strip() == '':
            return seek_line_parent(file_line, contents)

        # Known matches:
        #   - regular text
        #   - parent bullet
        elif NUMBERED_LIST_RE.match(contents[file_line].lstrip()):
            if leading_spaces(contents[file_line]) > leading_spaces(contents[line]):
                return [line]

    return []


def seek_line_parent(file_line, contents):
    for line in reversed(range(file_line)):

        # A header line is the only appropriate parent
        if contents[line].lstrip().startswith('#'):
            return [line]

    return []


def seek_header_parent(file_line, contents):

    def header_level(line):
        sline = line.lstrip()
        return len(sline) - len(sline.lstrip('#'))


    init = header_level(contents[file_line])

    # Header parent is any heading larger (smaller number) than current
    for line in reversed(range(file_line)):
        if (contents[line].lstrip().startswith('#') and
                header_level(contents[line]) < init):
            return [line]

    # No match
    return []


def obtain_implicit_references(file_line, contents):

    def get_switch(line):
        return line.lstrip()[0]

    switch = get_switch(contents[file_line])

    # TODO: Is multiple parents ever an option?

    ref_lines = None

    # Handle bullet points
    if switch in BULLET_MARKS:
        ref_lines = seek_list_parent(file_line, contents)

    # Handle numeric lists
    elif NUMBERED_LIST_RE.match(contents[file_line].lstrip()):
        ref_lines = seek_list_parent(file_line, contents)

    # Handle headings - TODO Setext headers
    elif switch == '#':
        ref_lines = seek_header_parent(file_line, contents)

    # default handling
    else:
        ref_lines = seek_line_parent(file_line, contents)

    return [generate_sha(line_to_parsetext(contents[i])) for i in ref_lines]

def is_line_requirement(i, line):
    # TODO
    return True

def line_to_parsetext(inputline):
    # Parse Markdown
    x = markdown.markdown(inputline)

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
    return generate_sha(requirement.parsedtext)

def generate_sha(requirement_text):
    inputtext = get_project_name() + requirement_text

    # TODO: Whats up with SHA-1 and unicode encoding?
    return hashlib.sha1(inputtext.encode('utf-8')).digest().hex()
