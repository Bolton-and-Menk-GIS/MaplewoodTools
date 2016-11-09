#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      calebma
#
# Created:     23/05/2016
# Copyright:   (c) calebma 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import datetime
import os
import sys
import arcpy
import zipfile
import fnmatch
import operator
import datetime
from dateutil.relativedelta import relativedelta

def remove_folders(path, days=7, exclude=[], older_than=True, test=False, subdirs=True, del_gdb=False):
    """removes old folders within a certain amount of days from today

    Required:
        path -- root directory to delete folders from
        days -- number of days back to delete from.  Anything older than
            this many days will be deleted. Default is 7 days.

    Optional:
        exclude -- list of folders to skip over (supports wildcards).
            These directories will not be removed.
        older_than -- option to remove all folders older than a certain
            amount of days. Default is True.  If False, will remove all
            folders within the last N days.
        test -- Default is False.  If True, performs a test folder iteration,
            to print out the mock results and does not actually delete folders.
        subdirs -- iterate through all sub-directories. Default is False.
        del_gdb -- delete file geodatabases. Default is False
    """

    # get removal date and operator
    remove_after = datetime.datetime.now() - relativedelta(days=days)
    op = operator.lt
    if not older_than:
        op = operator.gt

    # optional test
    if test:
        def remove(*args): pass
    else:
        def remove(*args):
            shutil.rmtree(args[0], ignore_errors=True)

    # walk thru directory
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if not d.endswith('.gdb'):
                if not any(map(lambda ex: fnmatch.fnmatch(d, ex), exclude)):
                    last_mod = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(root, d)))

                    # check date
                    if op(last_mod, remove_after):
                        try:
                            remove(os.path.join(root, d))
                            print 'deleted: "{0}"'.format(os.path.join(root, d))
                        except:
                            print '\nCould not delete: "{0}"!\n'.format(os.path.join(root, d))
                    else:
                        print 'skipped: "{0}"'.format(os.path.join(root, d))
                else:
                    print 'excluded: "{0}"'.format(os.path.join(root, d))
            else:
                if del_gdb:
                    remove(os.path.join(root, d))
                    print 'deleted geodatabase: "{0}"'.format(os.path.join(root, d))
                else:
                    print 'excluded geodatabase: "{0}"'.format(os.path.join(root, d))

        # break or continue if checking sub-directories
        if not subdirs:
            break

    return

def remove_files(path, days=7, exclude=[], older_than=True, test=False, subdirs=False):
    """removes old folders within a certain amount of days from today

    Required:
        path -- root directory to delete files from
        days -- number of days back to delete from.  Anything older than
            this many days will be deleted. Default is 7 days.

    Optional:
        exclude -- list of folders to skip over (supports wildcards).
            These directories will not be removed.
        older_than -- option to remove all folders older than a certain
            amount of days. Default is True.  If False, will remove all
            files within the last N days.
        test -- Default is False.  If True, performs a test folder iteration,
            to print out the mock results and does not actually delete files.
        subdirs -- iterate through all sub-directories. Default is False.
    """

    # get removal date and operator
    remove_after = datetime.datetime.now() - relativedelta(days=days)
    op = operator.lt
    if not older_than:
        op = operator.gt

    # optional test
    if test:
        'print testing....\n'
        def remove(*args): pass
    else:
        def remove(*args):
            os.remove(args[0])

    # walk thru directory
    for root, dirs, files in os.walk(path):
        if not root.endswith('.gdb'):
            for f in files:
                if not f.lower().endswith('.lock'):
                    if not any(map(lambda ex: fnmatch.fnmatch(f, ex), exclude)):
                        last_mod = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(root, f)))

                        # check date
                        if op(last_mod, remove_after):
                            try:
                                remove(os.path.join(root, f))
                                print 'deleted: "{0}"'.format(os.path.join(root, f))
                            except:
                                print '\nCould not delete: "{0}"!\n'.format(os.path.join(root, f))
                        else:
                            print 'skipped: "{0}"'.format(os.path.join(root, f))
                    else:
                        print 'excluded: "{0}"'.format(os.path.join(root, f))
                else:
                    print 'file is locked: "{0}"'.format(os.path.join(root, f))
        else:
            print 'excluded files in: "{0}"'.format(root)

        # break or continue if checking sub-directories
        if not subdirs:
            break

    return

def zipdir(path, out_zip=''):
    """zips a folder and all subfolders

    Required:
        path -- folder to zip

    Optional:
        out_zip -- output zip folder. Default is path + '.zip'
    """
    rootDIR = os.path.basename(path)
    if not out_zip:
        out_zip = path + '.zip'
    else:
        if not out_zip.strip().endswith('.zip'):
            out_zip = os.path.splitext(out_zip)[0] + '.zip'
    zipFile = zipfile.ZipFile(path + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for fl in files:
            if not fl.endswith('.lock'):
                subfolder = os.path.basename(root)
                if subfolder == rootDIR:
                    subfolder = ''
                zipFile.write(os.path.join(root, fl), os.path.join(subfolder, fl))
    return out_zip

def unzip(z, new=''):
    """unzip a zipped file

    Optional:
        new -- output folder, if not specified will default to same directory as zip
        folder.
    """
    if not new:
        new = os.path.splitext(z)[0]
    with zipfile.ZipFile(z, 'r') as f:
        f.extractall(new)
    return

def timeit(function):
    '''will time a function's execution time

    Required:
    function -- full namespace for a function

    Optional:
    args -- list of arguments for function
    '''
    st = datetime.datetime.now()
    def wrapper(*args, **kwargs):
        output = function(*args, **kwargs)
        Message('"{0}" from {1} Complete - Elapsed time: {2}'.format(function.__name__, sys.modules[function.__module__],
                                                            str(datetime.datetime.now()-st)[:-4]))
        return output
    return wrapper

def Message(*args):
    '''
    Prints message to Script tool window or python shell

    msg: message to be printed
    '''
    if isinstance(args, (list, tuple)):
        for msg in args:
            print str(msg)
            arcpy.AddMessage(str(msg))
    else:
        print str(msg)
        arcpy.AddMessage(str(msg))