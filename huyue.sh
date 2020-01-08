#!/usr/bin/env bash


ORIGINAL='/home/yuehu/Desktop/TestCode/test_git_vision_tools/original'
HEADERS_FOLDER_TO_PUBLISH='/home/yuehu/Desktop/TestCode/test_git_vision_tools/LiDAR_struct_lines_tracking_test'


if [ -e $HEADERS_FOLDER_TO_PUBLISH ]; then
  echo cleaning old HEADERS_FOLDER_TO_PUBLISH: $HEADERS_FOLDER_TO_PUBLISH
  rm -rf $HEADERS_FOLDER_TO_PUBLISH/*
else
  echo building HEADERS_FOLDER_TO_PUBLISH: $HEADERS_FOLDER_TO_PUBLISH
  mkdir -p $HEADERS_FOLDER_TO_PUBLISH
fi

cp -rp $ORIGINAL/interface/* $HEADERS_FOLDER_TO_PUBLISH
cp -rp $ORIGINAL/GX_ekf_pose $HEADERS_FOLDER_TO_PUBLISH



#param1='/home/yuehu/PycharmProjects/md5Test/group_list_cache.json'
#param2
#param3
#param4='/home/yuehu/PycharmProjects/trident_release'
#param5=$HEADERS_FOLDER_TO_PUBLISH

#python ./publish_libgroup.py --json-file $param1 --libs-list $_target_repo/tools/ci/usr_libs_list.txt --libs-folder $_strip_lib_folder --release-tool $param4 --headers-folder $param5 --publish-ws $_publish_ws --libgroup-name $_libgroup_name
#

