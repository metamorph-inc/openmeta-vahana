# author: tthomas@metamorphsoftware.com
# date:   2017-06-05
# description: automations script for converting '.m' files to python wrappers

import re
import sets

if __name__ == '__main__':
    component = ""
    params = list()
    unknowns = list()
    unknowns_set = sets.Set()
    with open('hoverPower.m', 'r') as fin:
        with open('output.py', 'w') as fout:
            text = fin.readlines()
            # Pass 1
            for line in text:
                m = re.match(r'function \[([\w,]+)\] = (\w+)\(([\w,]+)\)', line)
                if m is not None:
                    unknowns = list(m.group(1).split(','))
                    component = m.group(2)
                    params = list(m.group(3).split(','))
                else:
                    for unknown in unknowns:
                        if unknown in line:
                            m = re.findall('{}\\.(\\w+)'.format(unknown), line)
                            if m is not None:
                                unknowns_set = unknowns_set.union(m)
            
            print component
            print params
            print unknowns
            print unknowns_set
            
            # Pass 2
            for line in text:
                line = re.sub(r'^([ \t]*)%', r'\1#', line)
                line = re.sub(r'; %', r' #', line)
                line = re.sub(r';', r'', line)
                line.replace('^', '**')
                line.replace(' pi ', ' math.pi ')
                line.replace('sqrt(', 'math.sqrt(')
                line.replace('^', '**')
                fout.write(line)