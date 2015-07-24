import sys
import os
import lantern

def write_text_results(data, outfilename, encoding="utf-8"):
    with open(outfilename, "w") as f:
        f.write(data)
        print("Data written to {0}.".format(outfilename))


def write_binary_results(data, outfilename):
    with open(outfilename, "wb") as f:
        f.write(data)
        print("Data written to {0}.".format(outfilename))


username = os.environ['veracode_user']
password = os.environ['veracode_password']
app_name =  os.environ['veracode_app_name']
binaries_dir = os.environ['workspace']+ '/output'
build_name = os.environ['BUILD_NUMBER']
local_scan_delay = int(60)

global_black_list = ['*.DS_Store']
v = lantern.API(username, password, app_name, build_name)
v.upload_file_retry(binaries_dir, global_black_list)
v.begin_prescan(v.app_id, v.build_id, auto_scan=True)
prescan_results_filename = "{0}-PrescanResults-{1}.xml".format(app_name, build_name)
# try getting the results. Poll the Veracode service with an exponential backoff until we get results or until it fails.
prescan_results_xml = v.get_prescan_results(10, 0, 60, 2)  # max wait time = 34.1 hours + local_scan_delay
write_text_results(prescan_results_xml, prescan_results_filename)
