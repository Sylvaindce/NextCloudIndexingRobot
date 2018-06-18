import requests
from owncloud import *
import json
import config


class IndexingRobot:

    def login(self):
        self.oc.login(config.login, config.password)

    def logout(self):
        self.oc.logout()

    def get_ressources_from_path(self, path):
        return {'main_folder_info':self.oc.file_info(path), 'inside_folder_info':self.oc.list(path) }

    def generate_arch_json(self, main_folder_info, inside_folder_info):
        datas = []

        ##Construct content key for json_data
        folders_nbr = 0
        for tmp in inside_folder_info:
            data = {}
            data['fileid'] = tmp.get_fileid()
            data['name'] = tmp.get_name()
            data['type'] = tmp.get_content_type()
            data['path'] = tmp.get_path()
            data['etag'] = tmp.get_etag()
            data['size'] = tmp.get_size()
            if tmp.is_dir():
                folders_nbr += 1
                data['quota-used-bytes'] = tmp.get_quota_used_bytes()
            data['owner'] = tmp.get_owner_display_name()
            data['last_modified'] = tmp.get_last_modified_str()
            data['permissions'] = tmp.get_oc_permissions()
            datas.append(data)


        ## Construct main folder info for json_data
        data = {}
        data['fileid'] = main_folder_info.get_fileid()
        data['name'] = main_folder_info.get_name()
        data['type'] = main_folder_info.get_content_type()
        data['path'] = main_folder_info.get_path()
        data['etag'] = main_folder_info.get_etag()
        data['size'] = main_folder_info.get_size()
        data['quota-used-bytes'] = main_folder_info.get_quota_used_bytes()
        data['owner'] = main_folder_info.get_owner_display_name()
        data['total_elements_nbr'] = len(inside_folder_info)
        data['folders_nbr'] = folders_nbr
        data['files_nbr'] = len(inside_folder_info) - folders_nbr
        data['last_modified'] = main_folder_info.get_last_modified_str()
        data['permissions'] = main_folder_info.get_oc_permissions()
        data['content'] = datas

        ## Construct JSON object
        json_data = json.dumps(data, indent=4, sort_keys=True)
        return json_data


    def get_folders_from_specific_dir(self, folders):
        ## Recursive

        if (len(config.all_folders_path) is 0):
            config.all_folders_path.append(folders[0])

        if (len(folders) > 0):
            result = self.get_ressources_from_path(folders[0])
            folders.pop(0)
            for tmp in result['inside_folder_info']:
                if tmp.is_dir():
                    folders.append(tmp.get_path())
                    config.all_folders_path.append(tmp.get_path())
            self.get_folders_from_specific_dir(folders)
        else:
            config.all_folders_path = sorted(config.all_folders_path)
            print("#### ALL FOLDERS PATHS BEGIN ####")
            print(config.all_folders_path)
            print("#### ALL FOLDERS PATHS END ####\n")
            return 1

    def write_json_info_into_folder(self, path):
        result = self.get_ressources_from_path(path)
        json_data = self.generate_arch_json(result['main_folder_info'], result['inside_folder_info'])
        print("#### "+ path.upper() +" GENERATED JSON BEGIN ####")
        print(json_data)
        print("#### "+ path.upper() +" GENERATED JSON END ####\n")
        self.oc.put_file_contents(path+'/info.json', json_data)

    def generate_json_info_for_all_from_basedir(self):
        self.get_folders_from_specific_dir([config.basedir])

        #self.write_json_info_into_folder(path) for path in config.all_folders_path
        for path in config.all_folders_path:
            self.write_json_info_into_folder(path)
            print(path)

    def generate_json_folder(self, info):

        files = []
        files_nbr = 0
        folders = []

        for tmp in info['inside_folder_info']:
            data = {}
            if not tmp.is_dir():
                data['fileid'] = tmp.get_fileid()
                data['name'] = tmp.get_name()
                data['type'] = tmp.get_content_type()
                data['path'] = tmp.get_path()
                data['etag'] = tmp.get_etag()
                data['size'] = tmp.get_size()
                data['owner'] = tmp.get_owner_display_name()
                data['last_modified'] = tmp.get_last_modified_str()
                data['permissions'] = tmp.get_oc_permissions()
                files.append(data)
                files_nbr += 1
            else:
                data['fileid'] = tmp.get_fileid()
                data['name'] = tmp.get_name()
                data['type'] = tmp.get_content_type()
                data['path'] = tmp.get_path()
                data['etag'] = tmp.get_etag()
                data['size'] = tmp.get_size()
                data['quota-used-bytes'] = tmp.get_quota_used_bytes()
                data['owner'] = tmp.get_owner_display_name()
                data['total_elements_nbr'] = ""
                data['folders_nbr'] = ""
                data['files_nbr'] = ""
                data['last_modified'] = tmp.get_last_modified_str()
                data['permissions'] = tmp.get_oc_permissions()
                data['files'] = []
                data['folders'] = []
                folders.append(data)

        data = {}
        data['fileid'] = info['main_folder_info'].get_fileid()
        data['name'] = info['main_folder_info'].get_name()
        data['type'] = info['main_folder_info'].get_content_type()
        data['path'] = info['main_folder_info'].get_path()
        data['etag'] = info['main_folder_info'].get_etag()
        data['size'] = info['main_folder_info'].get_size()
        data['quota-used-bytes'] = info['main_folder_info'].get_quota_used_bytes()
        data['owner'] = info['main_folder_info'].get_owner_display_name()
        data['total_elements_nbr'] = len(info['inside_folder_info'])
        data['folders_nbr'] = len(info['inside_folder_info']) - files_nbr
        data['files_nbr'] = files_nbr
        data['last_modified'] = info['main_folder_info'].get_last_modified_str()
        data['permissions'] = info['main_folder_info'].get_oc_permissions()
        data['files'] = files
        if len(info['inside_folder_info']) - files_nbr is not 0:
            data['folders'] = folders

        ##json_data = json.dumps(data, indent=4, sort_keys=True)
        return data

    def map_rootdir_to_json(self, rootpath):
        self.get_folders_from_specific_dir([rootpath])
        all_jsons = []
        json_data = {}

        for i in enumerate(config.all_folders_path):
            print(i[1])
            toto = self.get_ressources_from_path(i[1])
            jojo = self.generate_json_folder(toto)
            all_jsons.append(jojo)
           
        json_data = all_jsons[0]
        for i in enumerate(all_jsons):
            for j in enumerate(json_data['folders']):
                if j[1]['path'] in i[1]['path']:
                    j[1].update(i[1])
                    # print(json.dumps(j[1], indent=4, sort_keys=True))

        ##json_data['folders'] = all_jsons[1]
        print(json.dumps(json_data, indent=4, sort_keys=True))

    def get_name_keys(self, _dict, _search):
        if _search in _dict['name']:
            print(_dict)
        else:
            self.get_name_keys(_dict['folders'], _search)

    def __init__(self):
        self.oc = Client(config.url)
        self.login()

def main():
    cloud = IndexingRobot()
    ##result = cloud.get_ressources_from_path(config.basedir)
    ##cloud.generate_json_info_for_all_from_basedir()
    ##cloud.get_folders_from_specific_dir([config.basedir])

    cloud.map_rootdir_to_json(config.basedir)

    cloud.logout()

if __name__ == "__main__":
    main()
