import os
import re
import sys
import platform


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


def run_desired_py_version(trident_path, py_v):
    if 'python2' == py_v:
        sys.path.append(os.path.join(trident_path, 'script'))
        from release_tool import Director
        from params_factory import SMB_LIBS_REPO, ALL_LIB_INDEX_JSON,LIB_MODE

        director = Director(SMB_LIBS_REPO, ALL_LIB_INDEX_JSON)
        print ('=======Publish Lib Group Automatically=======')
        director.auto_upload_by_list_json_as_group(LIB_MODE, smb_libs_repo=SMB_LIBS_REPO, group_list_json_path='/home/yuehu/PycharmProjects/md5Test/group_list_cache.json') # TODO given your group_list_json_path
    elif 'python3' == py_v:
        sys.path.append(os.path.join(trident_path, 'script_v3'))
        from release_tool import Director
        from params_factory import SMB_LIBS_REPO, ALL_LIB_INDEX_JSON, LIB_MODE

        director = Director(SMB_LIBS_REPO, ALL_LIB_INDEX_JSON)
        print ('=======Publish Lib Group Automatically=======')
        director.auto_upload_by_list_json_as_group(LIB_MODE, smb_libs_repo=SMB_LIBS_REPO, group_list_json_path='/home/yuehu/PycharmProjects/md5Test/group_list_cache.json')# TODO given your group_list_json_path

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



def main():
    screen_info_path = 'screen_info_temp.txt' # TODO give your path
    trident_path = '/home/yuehu/PycharmProjects/trident_release' # TODO give your path
    with open(screen_info_path, 'w') as fout:
        __console__ = sys.stdout  # store default sys.stdout: which is console
        sys.stdout = fout # write the 'print' info to file

        this_py_v = check_python_version()
        run_desired_py_version(trident_path, this_py_v)

    sys.stdout = __console__  # recover the default console

    YOUR_INFO = handle_log_file(screen_info_path) # TODO You can use this 'YOUR_INFO'
    print(YOUR_INFO)

    os.remove(screen_info_path) # delete temp file, depends on you~



if __name__ == '__main__':
    main()
