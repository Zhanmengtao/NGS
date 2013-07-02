#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import division, with_statement
'''
Copyright 2013, 陈同 (chentong_biology@163.com).  
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
'''
Functionla description

This is designed to normalize large regions to connected short
regions.

Input file format: (NOrmally the name of the peak is the forth column.
Duplicate names are allowed and will be connected as one peak. Also,
you can have other ways to redefine the name of your peak. For
example, you can use NM_029888_29995__11 as the name of your first two
peaks. All you need to do is to supply a separator<__> and the wanted
columns(1,2).)
chr1	74616752	74616877	NM_029888_29995__11__1	1.7	-
chr1	74616752	74616877	NM_029888_29995__11__2	1.7	-
chr1	74616752	74616877	NM_029888_29995__12__1	1.7	-
'''

import sys
import os
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP

def cmdparameter(argv):
    if len(argv) == 1:
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    desc = ""
    usages = "%prog -i file"
    parser = OP(usage=usages)
    parser.add_option("-i", "--input-file", dest="filein",
        metavar="FILEIN", help="A tab separated bed file. Only first 4 \
columns will be used,  other columns will be outputted as original.")
    parser.add_option("-n", "--norm-size", dest="ns",
        default=200, help="The length you want normalized regions to \
be. Default 200.")
    parser.add_option("-s", "--separator", dest="sep",
        default="__", help="The separtor to get part of strings in the \
forth column as peak names. Default '__'. If you want to use full \
string, supplies <"">(an empty string or other things that will be \
treated as FALSE) here.")
    parser.add_option("-c", "--columns", dest="col",
        default="1,2", help="The indexes of wanted parts in the list \
generated by string splitting. Default '1,2', representing the first \
and second element in the list. Here the number is 1-based.")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=0, help="Show process information")
    parser.add_option("-d", "--debug", dest="debug",
        default=False, help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------


def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    file = options.filein
    sep = options.sep
    if sep:
        col = [int(i)-1 for i in options.col.split(',')]
    else:
        col = ""
    norm_size = int(options.ns)
    verbose = options.verbose
    debug = options.debug
    #-----------------------------------
    if file == '-':
        fh = sys.stdin
    else:
        fh = open(file)
    #--------------------------------
    aDict = {}
    for line in fh:
        lineL = line.strip().split('\t')
        lineL[1] = int(lineL[1])
        lineL[2] = int(lineL[2])
        name = lineL[3]
        if sep:
            nameL = name.split(sep)
            tmpName = [nameL[i] for i in col]
            name = sep.join(tmpName)
        #-----------------------------------
        if name not in aDict:
            aDict[name] = []
        aDict[name].append(lineL[:])
    #-------------END reading file----------
    #----close file handle for files-----
    if file != '-':
        fh.close()
    #-----------end close fh-----------
    for name, valueL in aDict.items():
        if len(valueL) == 1:
            tmpLineL = valueL[0]
            start = tmpLineL[1]
            end   = tmpLineL[2]
            sum   = end - start 
            assert sum > 0, name
            cnt = 1
            if sum >= norm_size * 1.5:
                #tcnt = sum / norm_size
                for i in range(start, end, norm_size):
                    newstart = i
                    newend = newstart + norm_size
                    #print >>sys.stderr, newstart
                    #print >>sys.stderr, newend
                    if 0 < end - newend < norm_size * 0.5:
                        newend = end
                        #print >>sys.stderr, end
                        #print >>sys.stderr, 'here'
                    if newend > end:
                        newend = end
                    #print >>sys.stderr, newend
                    tmpLineL[1] = str(newstart)
                    tmpLineL[2] = str(newend)
                    tmpLineL[3] = name + sep + 'U' + str(cnt)
                    print '\t'.join(tmpLineL)
                    cnt += 1
                    if newend == end:
                        break
            else:
                tmpLineL[1] = str(tmpLineL[1])
                tmpLineL[2] = str(tmpLineL[2])
                tmpLineL[3] = name + sep + 'U' + str(cnt)
                print '\t'.join(tmpLineL)
        #--------END unspan exons---------------------------
        else:
            cnt = 1
            sum = 0
            valueL.sort(key=lambda x:(x[1], x[2]))
            for tmpL in valueL:
                sum += tmpL[2]-tmpL[1]
            if sum >= norm_size * 1.5:
                #tcnt = sum / norm_size + 1
                diff = norm_size
                #for i in range(tcnt):
                outputL = []
                lenvalueL = len(valueL)
                cntTmpL = 0
                for tmpL in valueL:
                    cntTmpL += 1
                    start = tmpL[1]
                    end   = tmpL[2]
                    die = 0
                    while (1):
                        die += 1
                        if (die > 10000):
                            print >>sys.stderr, "Forever loop %s" % tmpL
                            sys.exit(1)
                        newstart = start
                        newend = newstart + diff
                        if cntTmpL == lenvalueL and \
                            0 < end - newend < norm_size*0.5:
                            newend = end
                        if newend > end:
                            diff = newend - end
                            newend = end
                        else:
                            if diff != norm_size:
                                diff = norm_size
                        #-------------------------------- 
                        tmpL[1] = str(newstart)
                        tmpL[2] = str(newend)
                        #tmpL[3] = name
                        outputL.append(tmpL[:])
                        start = newend
                        if newend == end:
                            break
                    #-------------------------------
                #------------the last one---------
                #-output-------------------------------
                cnt159 = 1
                sum160 = 0
                innercnt = 1
                tmpsum187 = 0
                last192 = 0
                for tmpL in outputL[:-1]:
                    tmpsum187 += int(tmpL[2])-int(tmpL[1])
                    if sum - tmpsum187 < norm_size * 0.5:
                        last192 = 1
                    if last192 == 0 and sum160 == 0 and \
                        int(tmpL[2])-int(tmpL[1]) == norm_size:
                        tmpL[3] = name + sep + 'SU' + str(cnt159)
                    else:
                        tmpL[3] = name+sep+'S'+str(cnt159)+sep+str(innercnt)
                    #----------------------------------------------
                    print '\t'.join(tmpL)
                    innercnt += 1
                    sum160 += int(tmpL[2])-int(tmpL[1])
                    if last192 == 0 and sum160 % norm_size == 0:
                        sum160 = 0
                        cnt159 += 1
                        innercnt =1
                #--------------------The last one----------
                tmpL = outputL[-1]
                if last192 == 0 and sum160 == 0:
                    tmpL[3] = name + sep + 'SU' + str(cnt159)
                else:
                    tmpL[3] = name+sep+'S'+str(cnt159)+sep+str(innercnt)
                print '\t'.join(tmpL)
            #----------------------------------------
            else:
                cnt = 1
                for tmpL in valueL:
                    tmpL[1] = str(tmpL[1])
                    tmpL[2] = str(tmpL[2])
                    tmpL[3] = name + sep + 'S' + sep + str(cnt)
                    print '\t'.join(tmpL)
                    cnt += 1
    if verbose:
        print >>sys.stderr,\
            "--Successful %s" % strftime(timeformat, localtime())
if __name__ == '__main__':
    startTime = strftime(timeformat, localtime())
    main()
    endTime = strftime(timeformat, localtime())
    fh = open('python.log', 'a')
    print >>fh, "%s\n\tRun time : %s - %s " % \
        (' '.join(sys.argv), startTime, endTime)
    fh.close()



