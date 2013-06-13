import glob
import fnmatch
import os
import time
import xml.etree.ElementTree as ET
import ssl
import requests
from adapters import SSLAdapter


class ReceivedErrorXML(TypeError):
    pass


class ExceededRetries(StopIteration):
    pass


class FileNotFound(NameError):
    pass


class AbstractAPI():

    def __init__(self, username, password):
        self.base_url = "https://analysiscenter.veracode.com/api"
        self.set_credentials(username, password)

    def set_credentials(self, username, password):
        """
        Store the username and password for the api.
        """
        self.username = username
        self.password = password

    def get_credentials(self):
        return (self.username, self.password)

    def request(self, request_type, api, params=None, data=None, files=None, is_binary=False):
        """
        Return the xml result returned by a GET or POST call where one or more parameters can be a file.
        """
        url = "{}{}".format(self.base_url, api)

        """
        Mount a new SSLAdapter to the session
        because otherwise Python on Windows will fail.
        """
        s = requests.Session()
        s.mount('https://', SSLAdapter(ssl_version=ssl.PROTOCOL_TLSv1))

        r = s.request(request_type, url, params=params, data=data, files=files, auth=self.get_credentials())

        if is_binary:
            return r.content
        else:
            return r.text

    def detailed_report(self, build_id):
        """
        Get the detailed results of a build.
        build_id - ID of the build created by the uploadbuild call (returned in the build status xml).
        """
        return self.request("get", "/2.0/detailedreport.do", {"build_id": str(build_id)})

    def archer_report(self, app_id=None, period=None, from_date=None, to_date=None, scan_type=None):
        """Get the Archer report."""
        return self.request("get", "/archer.do",
            {'app_id': app_id, 'period': period, 'from_date': from_date, 'to_date': to_date, 'scan_type': scan_type})

    def begin_prescan(self, app_id, build_id=None):
        """
        Requires only app_id. build_id defaults to most recent. Returns the buildinfo xml.
        """
        return self.request("get", "/4.0/beginprescan.do", {'app_id': app_id, 'build_id': build_id})

    def begin_scan(self, app_id, modules=None, scan_all_top_level_modules=True):
        """
        Requires only app_id. Returns the buildinfo xml.
        """
        return self.request("get", "/4.0/beginscan.do",
            {'app_id': app_id, 'modules': modules, 'scan_all_top_level_modules': scan_all_top_level_modules})

    def create_app(self, app_name, business_criticality, description=None, vendor_id=None, policy=None,
                    business_unit=None, business_owner=None, business_owner_email=None, teams=None,
                    origin=None, industry=None, app_type=None, deployment_type=None, web_application=None,
                    archer_app_name=None, tags=None):
        """
        Creates an application. Requires only app_name and business_criticality. Returns the appinfo xml.
        """
        return self.request("get", "/4.0/createapp.do",
            {'app_name': app_name, 'business_criticality': business_criticality, 'description': description, 'vendor_id': vendor_id,
            'policy': policy, 'business_unit': business_unit, 'business_owner': business_owner, 'business_owner_email': business_owner_email,
            'teams': teams, 'origin': origin, 'industry': industry, 'app_type': app_type, 'deployment_type': deployment_type,
            'web_application': web_application, 'archer_app_name': archer_app_name, 'tags': tags})

    def create_build(self, app_id, version, lifecycle_stage=None, lifecycle_stage_id=None, launch_date=None):
        """
        Requires only app_id and version. Returns the buildinfo xml.
        """
        return self.request("get", "/4.0/createbuild.do",
            {'app_id': app_id, 'version': version, 'lifecycle_stage': lifecycle_stage,
             'lifecycle_stage_id': lifecycle_stage_id, 'launch_date': launch_date})

    def get_call_stacks(self, build_id, flaw_id):
        """
        The getcallstacks.do call returns the callstacks_[app_id]_[build_id]_[flaw_id] XML document, which references the callstacks.xsd schema.
        """
        return self.request("get", "/2.0/getcallstacks.do", {'build_id': build_id, 'flaw_id': flaw_id})

    def delete_app(self, app_id):
        """
        Requires only app_id. Deletes the app. Returns the applist xml.
        """
        return self.request("get", "/4.0/deleteapp.do", {'app_id': app_id})

    def delete_build(self, app_id):
        """
        Requires only app_id. Deletes the most recent build. Returns the applist xml.
        """
        return self.request("get", "/4.0/deletebuild.do", {'app_id': app_id})

    def get_app_builds(self):
        """
        Get the list of applications. Returns the applicationBuilds xml.
        """
        return self.request("get", "/2.0/getappbuilds.do")

    def get_app_info(self, app_id):
        """
        Requires only app_id. Returns the appinfo xml.
        """
        return self.request("get", "/4.0/getappinfo.do", {'app_id': app_id})

    def get_app_list(self):
        """
        No required paramaters. Returns the applist xml.
        """
        return self.request("get", "/4.0/getapplist.do")

    def get_build_info(self, app_id, build_id=None):
        """
        Requires only app_id. build_id defaults to most recent. Returns the buildinfo xml.
        """
        return self.request("get", "/4.0/getbuildinfo.do", {'app_id': app_id, 'build_id': build_id})

    def get_build_list(self, app_id):
        """
        Requires only app_id. Returns the buildlist xml.
        """
        return self.request("get", "/4.0/getbuildlist.do", {'app_id': app_id})

    def get_file_list(self, app_id, build_id=None):
        """
        Requires only app_id. build_id defaults to most recent. Returns the file list xml.
        """
        return self.request("get", "/4.0/getfilelist.do", {'app_id': app_id, 'build_id': build_id})

    def get_policy_list(self):
        """
        Provides a list of all the policies available for use by your account.
        It takes no parameters and returns the policy list xml.
        """
        return self.request("get", "/4.0/getpolicylist.do")

    def get_prescan_results(self, app_id, build_id=None):
        """
        Requires only app_id. build_id defaults to most recent. Returns the prescan results xml.
        """
        return self.request("get", "/4.0/getprescanresults.do", {'app_id': app_id, 'build_id': build_id})

    def get_vendor_list(self):
        """
        Requires no paramaters. Returns the vendorlist xml document.
        """
        return self.request("get", "/4.0/getvendorlist.do")

    def remove_file(self, app_id, file_id):
        """
        Removes a single file.  Returns the filelist xml.
        """
        return self.request("get", "/4.0/removefile.do", {'app_id': app_id, 'file_id': file_id})

    def summary_report(self, build_id):
        """
        Gets the summary results of a build.
        build_id is ID of the build created by the uploadbuild call (returned in the build status xml).
        """
        return self.request("get", "/2.0/summaryreport.do", {"build_id": str(build_id)})

    def detailed_report_pdf(self, build_id):
        """
        The detailedreportpdf.do call returns the detailedreport_[app_name]_[build_id]
        PDF format of the detailedreport XML file, which references the detailedreport.xsd schema.
        """
        return self.request("get", "/2.0/detailedreportpdf.do", {"build_id": str(build_id)}, is_binary=True)

    def summary_report_pdf(self, build_id):
        """
        The summaryreporttpdf.do call returns the summaryreport_[app_name]_[build_id]
        PDF format of the summaryreport XML file, which references the summaryreport.xsd schema.
        """
        return self.request("get", "/2.0/summaryreportpdf.do", {"build_id": str(build_id)}, is_binary=True)

    def third_party_report_pdf(self, build_id):
        """
        The thirdpartyreportpdf.do call returns the thirdpartyreport_[app_name]_[build_id]
        PDF format of the scan results of a third-party application.
        """
        return self.request("get", "/2.0/thirdpartyreportpdf.do", {"build_id": str(build_id)}, is_binary=True)

    def upload_file(self, app_id, filename):
        """
        Upload a single file. Returns the filelist xml.
        """
        with open(filename, "rb") as f:
            return self.request("post", "/4.0/uploadfile.do", data={"app_id": str(app_id)}, files={"file": f})

    def update_app(self, app_id, app_name=None, business_criticality=None,
                    policy=None, business_unit=None, business_owner=None,
                    business_owner_email=None, teams=None, origin=None, industry=None,
                    app_type=None, deployment_type=None, archer_app_name=None, tags=None,
                    custom_field_name=None, custom_field_value=None):
        """
        Updates the application with any amended information.  Requires only app_id.
        If custom_field_value or custom_field_name is present, the other is required. Returns appinfo xml.
        """
        return self.request("get", "/4.0/updateapp.do",
            {'app_id': app_id, 'app_name': app_name, 'business_criticality': business_criticality, 'policy': policy,
                'business_unit': business_unit, 'business_owner': business_owner, 'business_owner_email': business_owner_email,
                'teams': teams, 'origin': origin, 'industry': industry, 'app_type': app_type, 'deployment_type': deployment_type,
                'archer_app_name': archer_app_name, 'tags': tags, 'custom_field_name': custom_field_name, 'custom_field_value': custom_field_value})

    def update_build(self, app_id, build_id=None, version=None, lifecycle_stage=None, launch_date=None):
        """
        Updates the most recent build with amended information. If you want to update an earlier build, you must specify the build_id parameter.
        Requires only app_id. Returns updatebuild xml.
        """
        return self.request("get", "/4.0/updatebuild.do",
            {'app_id': app_id, 'build_id': build_id, 'version': version, 'lifecycle_stage': lifecycle_stage, 'launch_date': launch_date})


class API(AbstractAPI):
    def __init__(self, username, password, app_name, build_name):
        AbstractAPI.__init__(self, username, password)
        self.set_app_id(app_name)
        self.set_build_id(build_name)

    def set_app_id(self, app_name):
        print("Setting app_id.")
        app_list_xml = self.get_app_list()
        app_search_xpath = ".//{0}app[@app_name='{1}']".format(self.get_xml_namespace(app_list_xml), app_name)
        self.app_id = self.get_xml_attrib(app_list_xml, app_search_xpath, "app_id")

    def set_build_id(self, build_name):
        print("Setting build_id.")
        build_list_xml = self.create_build(build_name)
        build_search_xpath = ".//{0}build[@version='{1}']".format(self.get_xml_namespace(build_list_xml), build_name)
        self.build_id = self.get_xml_attrib(build_list_xml, build_search_xpath, "build_id")

    def create_build(self, build_name):
        build_list_xml = self.get_build_list(self.app_id)
        build_version_list = self.get_list_from_xml_attrib(build_list_xml, "version")

        if (build_name not in build_version_list):
            return AbstractAPI.create_build(self, self.app_id, build_name)
        else:
            return build_list_xml

    def create_black_list(self, directory, black_list_patterns):
        if black_list_patterns is None:
            return list()
        else:
            black_list = list()
            for pattern in black_list_patterns:
                glob_list = glob.glob(directory + pattern)
                for item in glob_list:
                    black_list.append(os.path.basename(item))
            return black_list

    def create_module_white_list(self, module_list, black_list_patterns):
        if black_list_patterns is None:
            return module_list
        else:
            modules = list(module_list)
            black_list = list()
            for module in modules:
                for pattern in black_list_patterns:
                    filtered_list = fnmatch.filter([module["module_name"]], pattern)
                    if filtered_list and module not in black_list:
                        black_list.append(module)
            for item in black_list:
                    modules.remove(item)
            return modules

    def compare_file_list(self, directory, black_list_patterns=None):
        master_file_list = self.get_master_file_list(directory)
        black_list = self.create_black_list(directory, black_list_patterns)
        white_list = list(set(master_file_list) - set(black_list))
        veracode_file_list_xml = self.get_file_list(self.app_id, self.build_id)
        veracode_file_list = self.get_list_from_xml_attrib(veracode_file_list_xml, "file_name")
        return list(set(white_list) ^ set(veracode_file_list))

    def compare_module_list(self, prescan_results_xml, black_list_patterns=None):
        veracode_module_list = self.get_module_list(prescan_results_xml)
        white_list = self.create_module_white_list(veracode_module_list, black_list_patterns)
        return white_list

    def get_build_info_status(self, build_info_xml):
        qualified_element_name = ".//{0}analysis_unit".format(self.get_xml_namespace(build_info_xml))
        return self.get_xml_attrib(build_info_xml, qualified_element_name, "status")

    def get_build_version(self, build_list_xml):
        qualified_element_name = ".//{0}build".format(self.get_xml_namespace(build_list_xml))
        return self.get_xml_attrib(build_list_xml, qualified_element_name, "version")

    def get_list_from_xml_attrib(self, xml, attrib):
        root = ET.fromstring(xml)
        return [child.get(attrib) for child in root]

    def get_master_file_list(self, directory):
        file_list = os.listdir(directory)
        master_file_list = list()
        for item in file_list:
            local_file = directory + '/' + item
            isfile = os.path.isfile(local_file)
            if isfile:
                master_file_list.append(item)
        return master_file_list

    def get_module_list(self, prescan_results_xml):
        module_list = list()
        root = ET.fromstring(prescan_results_xml)
        all_modules = root.findall(".{0}module".format(self.get_xml_namespace(prescan_results_xml)))
        for module in all_modules:
            module_id = module.get("id")
            module_name = module.get("name")
            module_list.append({"module_id": module_id, "module_name": module_name})
        return module_list

    def get_xml_attrib(self, appxml, xpath, attrib):
        root = ET.fromstring(appxml)
        if root.tag == "error":
            raise ReceivedErrorXML(root.text)
        element = root.find(xpath)
        return element.get(attrib)

    def get_xml_namespace(self, xml):
        root = ET.fromstring(xml)
        if root.tag == "error":
            raise ReceivedErrorXML(root.text)
        return root.tag.split("}", 1)[0] + '}'

    def poll_api(self, tries, initial_delay, delay, backoff, success_list, apifunction, *args):
        mdelay = delay  # make mutable
        time.sleep(initial_delay)
        for n in range(tries):
            build_status = self.get_build_info_status(self.get_build_info(self.app_id, self.build_id))
            if build_status not in success_list:
                polling_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
                print("{0}. Sleeping for {1} seconds.".format(polling_time, mdelay))
                time.sleep(mdelay)
                mdelay *= backoff
            else:
                return apifunction(*args)
        raise ExceededRetries("Failed to poll {0} within {1} tries.".format(apifunction, tries))

    def veracode_files_number(self):
        veracode_file_list_xml = self.get_file_list(self.app_id, self.build_id)
        root = ET.fromstring(veracode_file_list_xml)
        return len(list(root.iter()))

    def begin_scan(self, prescan_results_xml, black_list_patterns=None):
        white_list = self.compare_module_list(prescan_results_xml, black_list_patterns)
        module_id_list = [item["module_id"] for item in white_list]
        if len(module_id_list) > 100:  # Veracode can't handle large numbers of modules in this request.
            return AbstractAPI.begin_scan(self, self.app_id)
        else:
            modules = ", ".join(module_id_list)
            return AbstractAPI.begin_scan(self, self.app_id, modules, False)

    def get_prescan_results(self, tries=1, initial_delay=0, delay=1, backoff=2):
        success_list = ["Pre-Scan Success", "Results Ready", "Scan Internal Error"]
        return self.poll_api(tries, initial_delay, delay, backoff, success_list, AbstractAPI.get_prescan_results, self, self.app_id, self.build_id)

    def remove_file_by_name(self, filename):
        print("Removing {0}.".format(filename))
        veracode_file_list_xml = self.get_file_list(self.app_id, self.build_id)
        root = ET.fromstring(veracode_file_list_xml)
        for child in root:
            if child.get("file_name") == filename:
                file_id = child.get("file_id")
                return AbstractAPI.remove_file(self.app_id, file_id)
        raise FileNotFound("{0} not found.".format(filename))

    def remove_file(self):
        veracode_file_list_xml = self.get_file_list(self.app_id, self.build_id)
        root = ET.fromstring(veracode_file_list_xml)
        count = self.veracode_files_number()
        file_list_xml = None
        print("Removing {0} files.".format(count))
        for child in root:
            file_id = child.get("file_id")
            file_list_xml = AbstractAPI.remove_file(self, self.app_id, file_id)
        return file_list_xml

    def remove_file_retry(self, number_retries=100):
        return self.retry(number_retries, self.remove_file)

    def retry(self, number_retries, function, *args):
        for item in range(number_retries):
            result = function(*args)
            if result:
                return result
            if ((item == (number_retries - 1)) and (not result)):
                raise ExceededRetries("Failed to call {0} within {1} retries.".format(function, number_retries))

    def upload_file(self, binaries_dir, black_list_patterns=None):
        files = self.compare_file_list(binaries_dir, black_list_patterns)
        if not files:
            print("No files to upload. Returning filelist xml.")
            return self.get_file_list(self.app_id, self.build_id)
        file_list_xml = None
        print("Uploading {0} files. Files: {1}".format(len(files), files))
        for item in files:
            local_file = binaries_dir + '/' + item
            file_list_xml = AbstractAPI.upload_file(self, self.app_id, local_file)
        return file_list_xml

    def upload_file_retry(self, binaries_dir, black_list_patterns=None, number_retries=10):
        """
        Retries to upload files until the number of retries has been exceeded.
        In addition, if the files did not fail and still did not upload successfully,
        it attempts to recursively retry until all files are uploaded successfully or
        until the number of retries is exceeded.

        It's necessary to do this check and recursively retry because even if your files
        upload successfully, errors may occur on Veracode's server that prevent files
        from populating correctly on Veracode's side.
        """
        file_list_xml = self.retry(number_retries, self.upload_file, binaries_dir, black_list_patterns)
        compared_list = self.compare_file_list(binaries_dir, black_list_patterns)
        if compared_list != []:
            self.retry(number_retries, self.upload_file_retry, binaries_dir, black_list_patterns, number_retries - 1)
        else:
            return file_list_xml

    def detailed_report(self, tries=1, initial_delay=0, delay=1, backoff=2):
        success_list = ["Results Ready"]
        return self.poll_api(tries, initial_delay, delay, backoff, success_list, AbstractAPI.detailed_report, self, self.build_id)

    def detailed_report_pdf(self, tries=1, initial_delay=0, delay=1, backoff=2):
        success_list = ["Results Ready"]
        return self.poll_api(tries, initial_delay, delay, backoff, success_list, AbstractAPI.detailed_report_pdf, self, self.build_id)

    def summary_report(self, tries=1, initial_delay=0, delay=1, backoff=2):
        success_list = ["Results Ready"]
        return self.poll_api(tries, initial_delay, delay, backoff, success_list, AbstractAPI.summary_report, self, self.build_id)

    def summary_report_pdf(self, tries=1, initial_delay=0, delay=1, backoff=2):
        success_list = ["Results Ready"]
        return self.poll_api(tries, initial_delay, delay, backoff, success_list, AbstractAPI.summary_report_pdf, self, self.build_id)

    def third_party_report_pdf(self, tries=1, initial_delay=0, delay=1, backoff=2):
        success_list = ["Results Ready"]
        return self.poll_api(tries, initial_delay, delay, backoff, success_list, AbstractAPI.third_party_report_pdf, self, self.build_id)
