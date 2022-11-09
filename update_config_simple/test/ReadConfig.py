#!/usr/bin/env python
import json
import os.path


def main():
    strFileName = "/home/mogo/data/UpdateConfig.json"
    strFileContent = ""
    if not os.path.exists(strFileName):
        return
    fileObject = open(strFileName, "r")
    try:
        strFileContent = fileObject.read()
    except Exception as e:
        print(str(e))
    finally:
        fileObject.close()
    if len(strFileContent) > 0:
        dictConfig = json.loads(strFileContent)
        print("url_list:{0}".format(dictConfig['url_list']))
        print("url_sync:{0}".format(dictConfig['url_sync']))



if __name__ == "__main__":
    main()
