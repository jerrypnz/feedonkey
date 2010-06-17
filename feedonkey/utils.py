from feedonkey.logger import log

#--- Helper functions ----------------------------------------------

def line_token_iterator(file, separator=None, support_comment=False, comment_char='#'):
    """convenient file iterator that could separate the lines with given separator
    and ignore comments"""
    try:
        for line in open(file):
            if support_comment:
                com_pos = line.find(comment_char)
                if com_pos >=0:
                    line = line[:com_pos]

            parts = line.split(separator)
            if len(parts) > 0:
                yield tuple(parts)

    except IOError, e:
        log.error('error reading file %s' % file, e)


