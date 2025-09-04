#!/usr/bin/env python

import numpy as np
import sys

def my_patch(inputFilename, R_scale, B_scale):

    def unit_scaling(l,scalefactor):
        if scale is not None:
            raise ValueError("Scale is not None. This shouldn't happen.")
        return l


    def rescale_followup(l,scalefactor,formatter="{: .15e}".format):
        vals = l.split()
        new_vals = []
        for val in vals:
            if val[-1] == ",":
                val = val[:-1]
            new_vals.append(float(val))
        try:
            new_vals = np.array(new_vals) * scalefactor
        except:
            print(new_vals)
            raise ValueError
        new_line = ' '.join([formatter(val) for val in new_vals])
        if l[-1] == '\n':
            new_line = new_line + '\n'
        return new_line
        
    
    def rescale_multiarrayline(l,scalefactor,formatter="{: .15e}".format):
        sl = l.split("=")
        keys = []
        values = []
        keys.append(sl[0])
        for i in range(1,len(sl)-1):
            ssl = sl[i].split(None,1)
            val = ssl[0]
            if val[-1] == ',':
                val = val[:-1]
            values.append(float(val))
            key = ssl[1]
            keys.append(key)
        values.append(float(sl[-1]))
        values = np.array(values) * scalefactor
        new_line = ',      '.join([key + " = " + formatter(val) for (key,val) in zip(keys,values)])
        if l[-1] == '\n':
            new_line = new_line + '\n'
        return new_line

    def rescale_arrayline(l,scalefactor,formatter="{: .15e}".format):
        sl = l.split("=")
        key = sl[0]
        vals = sl[1].split()
        new_vals = []
        for val in vals:
            if val[-1] == ",":
                val = val[:-1]
            new_vals.append(float(val))
        try:
            new_vals = np.array(new_vals) * scalefactor
        except:
            print(new_vals)
            raise ValueError
        new_line = key + " = " +  ' '.join([formatter(val) for val in new_vals])
        if l[-1] == '\n':
            new_line = new_line + '\n'
        return new_line
        
    with open(inputFilename,"r") as f:
        lines = f.readlines()
        new_lines = []
        for line in lines:
            ls = line.split("!", 1)
            if len(ls) > 1:
                comment = ls[1]
            else:
                comment = ""
            line = ls[0]
            l = line.strip().lower()

            if len(l) == 0:
                # empty line
                new_line = line
            elif l[0] == "&":
                # group name
                new_line = line
            elif l[0] == "/":
                # end of group
                new_line = line
            elif "=" in l:
                # a new variable is defined on this line
                # if the variable matches any of these, we rescale it
                if l[:3] == "rbc" or l[:3] == "zbs" or l[:3] == "rbs" or l[:3] == "zbc":
                    new_line = rescale_multiarrayline(line,R_scale)
                    scale = R_scale
                    func = rescale_multiarrayline
                elif l[:5] == "raxis":
                    new_line = rescale_arrayline(line,R_scale)
                    scale = R_scale
                    func = rescale_arrayline
                elif l[:8] == "raxis_cc":
                    new_line = rescale_arrayline(line,R_scale)
                    scale = R_scale
                    func = rescale_arrayline
                elif l[:5] == "zaxis":
                    new_line = rescale_arrayline(line,R_scale)
                    scale = R_scale
                    func = rescale_arrayline
                elif l[:8] == "zaxis_cc":
                    new_line = rescale_arrayline(line,R_scale)
                    scale = R_scale
                    func = rescale_arrayline
                elif l[:7] == "phiedge":
                    new_line = rescale_arrayline(line,B_scale*R_scale**2)
                    scale = B_scale*R_scale**2
                    func = rescale_arrayline
                elif l[:10] == "pres_scale":
                    new_line = rescale_arrayline(line,B_scale**2)
                    scale = B_scale**2
                    func = rescale_arrayline
                elif l[:6] == "curtor":
                    new_line = rescale_arrayline(line,B_scale*R_scale)
                    scale = B_scale*R_scale
                    func = rescale_arrayline
                elif l[:2] == "ac":
                    new_line = rescale_arrayline(line,B_scale/R_scale)
                    scale = B_scale/R_scale
                    func = rescale_arrayline
                elif l[:2] == "am":
                    new_line = rescale_arrayline(line,B_scale**2)
                    scale = B_scale**2
                    func = rescale_arrayline

                else:
                    # if the variable did not match, we do not rescale
                    func = unit_scaling
                    scale = 1.0
                    new_line = line
            elif len(l) > 0:
                # no new variable is defined, but it's not an empty line or group header/footer
                # so assume this is a continuation of the previous line
                new_line = rescale_followup(line,scale)
            
                
            if len(comment) > 0:
                # comments include their newline
                new_line = new_line + " !" + comment
            new_lines.append(new_line)
    return new_lines    


def scale_vmec(inputFilename, B_scale, R_scale, outputFilename=None):
    if outputFilename is None:
        outputFilename = inputFilename + "_scaled"


    new_lines = my_patch(inputFilename, R_scale, B_scale)
    with open(outputFilename,'w') as f:
        f.writelines(new_lines)


if __name__ == "__main__":
    print("Usage: ./scale_vmec.py input.* B_scale R_scale [output name]")
    if len(sys.argv) < 4:
        exit(0)

    if len(sys.argv) == 5:
        outputFilename = sys.argv[4]
    else:
        outputFilename = None
    inputFilename = sys.argv[1]
    B_scale = float(sys.argv[2])
    R_scale = float(sys.argv[3])
    
    print("B_scale =" + str(B_scale) + " R_scale =" + str(R_scale))

    scale_vmec(inputFilename, B_scale, R_scale, outputFilename)
