#!/usr/bin/env python
# coding: utf-8

"""generate the json file required by vision_algo_release_tool"""

from __future__ import print_function

import argparse
import os
import re
import platform
import json
import shutil
import sys
from enum import Enum


def check_python_version():
    python_version=platform.python_version()
    python_v_list = python_version.split('.')
    python_v_key = python_v_list[0]

    if python_v_key == '2':
        print (">>> You are using Python {}".format(python_version))
        return 'python2'
    elif python_v_key == '3':
        print (">>> You are using Python {}".format(python_version))
        return 'python3'
    else:
        print (">>> Unknow Python version, make sure you use python2 or python3!")
        exit(-1)


def run_desired_py_version(trident_path, py_v, group_list_json_path):
    if 'python2' == py_v:
        sys.path.append(os.path.join(trident_path, 'script'))
        from release_tool import Director
        from params_factory import SMB_LIBS_REPO, ALL_LIB_INDEX_JSON,LIB_MODE

        director = Director(SMB_LIBS_REPO, ALL_LIB_INDEX_JSON)
        print ('=======Publish Lib Group Automatically=======')
        director.auto_upload_by_list_json_as_group(LIB_MODE, smb_libs_repo=SMB_LIBS_REPO, group_list_json_path=group_list_json_path) # TODO given your group_list_json_path
    elif 'python3' == py_v:
        sys.path.append(os.path.join(trident_path, 'script_v3'))
        from release_tool import Director
        from params_factory import SMB_LIBS_REPO, ALL_LIB_INDEX_JSON, LIB_MODE

        director = Director(SMB_LIBS_REPO, ALL_LIB_INDEX_JSON)
        print ('=======Publish Lib Group Automatically=======')
        director.auto_upload_by_list_json_as_group(LIB_MODE, smb_libs_repo=SMB_LIBS_REPO, group_list_json_path=group_list_json_path)# TODO given your group_list_json_path

def return_line_num(desired_str, str_list):
    line_num = 0
    for line in str_list:
        if desired_str in line:
            return line_num

        line_num += 1
    return -1

def get_group_version(str_list):
    group_v = ''
    for line in str_list:
        if ">>> New version:" in line:
            temp = line.strip('\n').split(':')
            group_v = temp[1].strip(' ')
    return group_v

def extract_libName(str_line):
    libName = ''
    searchObj = re.search(r">>> Lib '(.*)' is", str_line, re.M | re.I)
    libName = searchObj.group(1)
    return libName

def extract_libStatus(str_line):
    if 'not changed' in str_line:
        return 'unchanged'
    elif 'successful' in str_line:
        return 'success'
    else:
        return 'unknown'

def extract_lib_currVersion(str_line):
    curr_v = ''
    if 'current version' in str_line:
        curr_v = str_line.split(':')[1].strip(' ')
    return curr_v

def extract_lib_preVersion(str_line):
    pre_v = ''
    if 'previous version' in str_line:
        pre_v = str_line.split(':')[1].strip(' ')
    return pre_v


def get_group_lib_info(log_path):
    group_info = dict()
    group_info['groupName'] = ''
    group_info['groupVersion'] = ''

    lib_list = []

    with open(log_path, 'r') as fin:
        lines = fin.readlines()
        n = return_line_num('--- Group info from list ---', lines)
        group_info['groupVersion'] = get_group_version(lines[n:])

        # handle group info
        for line in lines:
            if 'Group name:' in line:
                group_name = line.strip('\n').split()[-1]
                group_info['groupName'] = group_name


        n2 = return_line_num('------  LOG  ------', lines)
        n3 = return_line_num('=== Procesing group ...... ===', lines)

        # handle lib info
        for line in lines[n2: n3]:
            if '>>> Lib' in line:
                libName = extract_libName(line.strip('\n'))
                libStatus = extract_libStatus(line.strip('\n'))
                currVersion = extract_lib_currVersion(line.strip('\n'))
                preVersion = extract_lib_preVersion(line.strip('\n'))

                lib_dict = dict()
                lib_dict['libName'] = libName
                lib_dict['libStatus'] = libStatus
                lib_dict['current_version'] = currVersion
                lib_dict['previous_version'] = preVersion
                lib_list.append(lib_dict)

    return group_info, lib_list



def handle_log_file(log_path):
    res_dict = dict()
    res_dict['status_detail'] = []
    res_dict['group'] = dict()
    res_dict['sub_libs'] = []

    with open(log_path, 'r') as fin:
        lines = fin.readlines()
        for line in lines:
            if '>>> Please check your list_cache.json file' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append('group_list_cache.json is not existed')
            elif '>>> the smb is busy or empty, exit now...' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif '>>> Failed! Some info are missing, please check your file' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif '>>> Lib path not exist!' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif '>>> Your workspace is not clean, use "git commit -m " first' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif '>>> Error! Please check your group, maybe there is no group or more than one group!' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif '>>> Error! When check group info, path is not existed:' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif '>>> Error! When check group info, git path can not be empty!' in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif "Error! 'group_name' is missed. Please check 'group_list_cache.json'" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif "Error! 'group_version' is missed. Please check 'group_list_cache.json'" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif "Error! 'group_version' is missed. Please check 'group_list_cache.json'" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif "Error! 'incld_path' is missed. Please check 'group_list_cache.json'" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>>Error! Group include file output path is none. Please check 'group_list_cache.json'" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>>Error! Please make sure the input path is in git project, thanks!" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>> Error! zip path is empty!" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>>Error! group version has something wrong, please check!" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>> Error!" in line and "platform_type:" in line and "is not valid! please check your file!" in line:
                res_dict['status'] = 'error'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>>Unfortunately! Your group(.zip) or any of sub libs are not changed! Please update it and then push it!!!" in line:
                res_dict['status'] = 'unchanged'
                res_dict['status_detail'].append(line.strip('\n'))
            elif ">>> Good!" in line and "info is no problem and its changed!" in line:
                res_dict['status'] = 'success'
                res_dict['status_detail'].append(line.strip('\n'))

    group_info, lib_list = get_group_lib_info(log_path)
    res_dict['group'] = group_info
    res_dict['sub_libs'] = lib_list
    return res_dict




######################################

PlatformType__x86_64_and_arm_v8a = "x86_64_and_arm64-v8a"
PlatformType__x86_64_only = "x86_64_only"
PlatformType__arm_v8a_only = "arm64-v8a_only"

def get_platform_list(platform_type):
  """ each platform-type corresponds to a certain platform list """
  x86_64_platform = "x86_64"
  arm_v8a_platform = "arm64-v8a"
  if platform_type == PlatformType__x86_64_and_arm_v8a:
    return [x86_64_platform, arm_v8a_platform]
  elif platform_type == PlatformType__x86_64_only:
    return [x86_64_platform,]
  elif platform_type == PlatformType__arm_v8a_only:
    return [arm_v8a_only,]
  else:
    return []

### the method "zipdir" will be removed from this module in future since
### they are common methods shared by multiple modules.
import zipfile
def zipdir(src, dst, exclude_dirs=None):
  """input: src directory to be zipped
   dst fullname of the zip file without extension
   exclude_dirs, names of subdirectories to be excluded from zipping
  """
  if exclude_dirs is None:
    exclude_dirs = []
  zfile = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
  abs_src = os.path.abspath(src)
  for dirname, subdirs, files in os.walk(src):
    for skip_dir in exclude_dirs:
      if skip_dir in subdirs:
        subdirs.remove(skip_dir)
    for filename in files:
      absname = os.path.abspath(os.path.join(dirname, filename))
      arcname = absname[len(abs_src) + 1:]
      zfile.write(absname, arcname)
  zfile.close()


def generate_upload_json_for_grouped_libs(
    group_name,
    liblistfile,
    libdirname,
    platform_type,
    headerdirname,
    jsonfilename):
  """
  generate the json file used for publishing a version of libs from a text
   file containing the list of libraries
  In the file each line is the exact library name, e.g., libaslam_cv_matcher.so
  libdirname is the folder of all the libs in the file
  jsonfilename is the output json file for the listed libraries
  """
  platforms = get_platform_list(platform_type)
  libnames = list()
  with open(liblistfile, 'r') as stream:
    for line in stream:
      lib_name = line.strip('\n')
      if lib_name[0] != '#':
        libnames.append(lib_name)

  with open(jsonfilename, 'w') as stream:
    stream.write('[\n')
    indentcount = 4

    stream.write("{}{{\n".format(' ' * indentcount))
    stream.write("{}\"group_name\":\"{}\",\n".format(' '*indentcount*2, group_name))
    stream.write("{}\"group_version\":\"newest\",\n".format(' '*indentcount*2))

    stream.write("{}\"incld_path\":\"{}\"\n".
                 format(' ' * indentcount * 2, headerdirname))
    stream.write("{}}},\n".format(' ' * indentcount))

    for index, lib_name in enumerate(libnames):
      stream.write("{}{{\n".format(' '*indentcount))
      stream.write("{}{}\"lib_name\":\"{}\",\n".
                   format(' '*indentcount, ' '*indentcount, lib_name))
      stream.write("{}{}\"version\":\"newest\",\n".
                   format(' ' * indentcount, ' ' * indentcount))
      #stream.write("{}{}\"path\":\"{}\"\n".
      #             format(' ' * indentcount, ' ' * indentcount,
      #                    os.path.join(libdirname, lib_name)))
      stream.write("{}{}\"paths\": [".format(' ' * indentcount, ' ' * indentcount))
      for jack, platform in enumerate(platforms):
        if jack != 0:
          stream.write(", ")
        path = os.path.join(libdirname, platform, lib_name)
        stream.write("{{\"platform\": \"{}\", \"path\": \"{}\"}}".format(platform, path))
      stream.write("],\n")
      stream.write("{}{}\"platform_type\": \"{}\"\n".format(
          ' ' * indentcount, ' ' * indentcount, platform_type))

      if index == len(libnames) - 1:
        stream.write("{}}}\n".format(' ' * indentcount))
      else:
        stream.write("{}}},\n".format(' ' * indentcount))
    stream.write(']\n')


def parse_args():
  """parse arguments"""
  parser = argparse.ArgumentParser(
      description='generate json file for the release tool')

  parser.add_argument(
      '--json-file', metavar='json_file', nargs='?',
      #default='/vision_algo_lib_release_tool/script/group_list_cache.json',
      default='group_list_cache.json',
      help='the output json filename(default: %(default)s).',
      required=False)

  parser.add_argument(
      '--platform-type', metavar='platform_type', nargs='?',
      #default='/vision_algo_lib_release_tool/script/group_list_cache.json',
      default=PlatformType__x86_64_and_arm_v8a,
      help='platform type, available options: {}, {}, {}'.format(
          PlatformType__x86_64_and_arm_v8a, PlatformType__x86_64_only, PlatformType__arm_v8a_only),
      required=False)

  parser.add_argument(
      '--libs-folder', metavar='libs_folder', nargs='?',
      help='the folder contains all libs waiting for publishing'
           '(default: %(default)s).',
      default='/persist/maplab_ws/src/algo_dependencies/lib/')

  parser.add_argument(
      '--headers-folder', metavar='headers_folder', nargs='?',
      help='the folder contains the headers waiting for publishing'
           '(default: %(default)s).',
      default='/persist/maplab_ws/src/algo_dependencies/algo_dependencies_android/interface')

  parser.add_argument(
      '--libgroup-name', metavar='libgroup_name', nargs='?',
      help='name of the library group',
      default="algo_dependencies")

  parser.add_argument(
      '--publish-ws', metavar='publish_ws', nargs='?',
      help='publish workspace folder, which already contains commit.log and changelog.log in it',
      default="/persist/data/workspace/algo_dependencies_segway_publish")

  parser.add_argument(
      '--libs-list', metavar='libs_list', nargs='?',
      help='filename of the list of libraries(default: %(default)s)',
      default='/persist/maplab_ws/src/algo_dependencies/tools/ci/usr_libs_list.txt')

  parser.add_argument(
      '--release-tool', metavar='release_tool', nargs='?',
      help='the folder of the trident_release'
           '(default: %(default)s).',
      required=True)

  parsed = parser.parse_args()

  if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)
  return parsed

def find_filename_of_pattern(mypath, patterns):
  """find all filenames in a folder matching patterns.
  Not go into subfolders"""
  onlyfiles = [os.path.join(mypath, filename)
               for filename in os.listdir(mypath) if
               os.path.isfile(os.path.join(mypath, filename))]
  foundfilelist = list()
  for pat in patterns:
    foundfilelist.append(list())

  for filepath in onlyfiles:
    filename = os.path.basename(filepath)
    for index, pat in enumerate(patterns):
      if re.search(pat, filename) is not None:
        foundfilelist[index].append(filepath)
        break
  return foundfilelist


def main():
  """main function"""
  parsed = parse_args()
  if len(get_platform_list(parsed.platform_type)) == 0:
    print("Illegal platform_type !")
    return 2

  publish_ws = parsed.publish_ws
  commitlog = os.path.join(publish_ws, "commit.log")
  changelog = os.path.join(publish_ws, "changelog.log")

  tempfolder = os.path.join(publish_ws, 'temp')
  if os.path.exists(tempfolder):
    shutil.rmtree(tempfolder)
  os.mkdir(tempfolder)

  orig_stdout = sys.stdout
  logfile = os.path.join(tempfolder, "release_tool.log")
  logstream = open(logfile, 'w')
  sys.stdout = logstream

  generate_upload_json_for_grouped_libs(
    parsed.libgroup_name, parsed.libs_list, parsed.libs_folder,
    parsed.platform_type, parsed.headers_folder, parsed.json_file)

  print("=======Publish Lib Group Automatically=======")
  this_py_v = check_python_version()
  run_desired_py_version(parsed.release_tool, this_py_v, parsed.json_file)
  #repo_control.auto_upload_by_list_json_as_group_with_param(parsed.json_file, publish_ws)
  sys.stdout = orig_stdout
  logstream.close()

  PUBLISH_INFO = handle_log_file(logfile)
  print(PUBLISH_INFO)

  try:
    with open(os.path.join(publish_ws, "publish_info.json"), "w") as stream:
      json.dump(PUBLISH_INFO, stream, indent=2)
  except IOError as err:
    print(err)

  try:
    shutil.copy(os.path.join(publish_ws, "log_build.txt"),
                os.path.join(tempfolder, "log_build.txt"))
  except IOError as err:
    print(err)
  try:
    shutil.copyfile(commitlog, os.path.join(tempfolder, 'commit.log'))
  except IOError as err:
    print(err)
  try:
    shutil.copyfile(changelog, os.path.join(tempfolder, 'changelog.log'))
  except IOError as err:
    print(err)

  zipfilename = os.path.join(publish_ws, "publish_log")
  zipdir(tempfolder, zipfilename)
  print("The publishing log {} and auto generated json {} are "
        "zipped in {}.zip\n".format(logfile, parsed.json_file, zipfilename))

  if PUBLISH_INFO["status"] == "success":
    print("Succeeded to publish the {} libraries ({})!".format(PUBLISH_INFO["group"]["groupName"], PUBLISH_INFO["group"]["groupVersion"]))
    return 0
  elif PUBLISH_INFO["status"] == "unchanged":
    print("Lib group {} is unchanged!".format(PUBLISH_INFO["group"]["groupName"]))
    return 0
  else:
    print("Failed to publish the {} libraries!".format(PUBLISH_INFO["group"]["groupName"]))
    return 1

if __name__ == "__main__":
  sys.exit(main())
