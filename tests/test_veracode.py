import os
import sys
sys.path.append(os.getcwd())
from lantern import *
import requests
import nose.tools
from mock import patch

# mock data. These are real xml examples that have been scrubbed for personal information that represent actual xml responses from Veracode.

mock_app_builds_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<applicationbuilds xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/applicationbuilds" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/applicationbuilds https://analysiscenter.veracode.com/resource/2.0/applicationbuilds.xsd" '
    'account_id="00001">'
    '<application app_name="TestApp" app_id="00001" industry_vertical="Software" assurance_level="High" business_criticality="High" origin="Internally Developed" '
    'modified_date="2010-09-17T11:43:22-04:00" cots="false" business_unit="Not Specified" tags="">'
    '<customfield name="Custom 1" value=""/>'
    '<customfield name="Custom 2" value=""/>'
    '<customfield name="Custom 3" value=""/>'
    '<customfield name="Custom 4" value=""/>'
    '<customfield name="Custom 5" value=""/>'
    '<build version="5.0.0.3232" build_id="12724" submitter="my submitter" platform="Windows" lifecycle_stage="External or Beta Testing" '
    'results_ready="true" policy_name="Veracode Transitional High" policy_version="1" policy_compliance_status="Did Not Pass" rules_status="Did Not Pass" '
    'grace_period_expired="false" scan_overdue="false">'
    '<analysis_unit analysis_type="Static" published_date="2008-11-26T14:43:43-05:00" published_date_sec="1227728623" status="Results Ready"/>'
    '</build></application>'
    '<application app_name="TestApp2" app_id="00002" industry_vertical="Technology" assurance_level="High" business_criticality="High" origin="Not Specified" '
    'modified_date="2012-11-21T09:47:57-05:00" cots="false" business_unit="Not Specified" tags="">'
    '<customfield name="Custom 1" value=""/>'
    '<customfield name="Custom 2" value=""/>'
    '<customfield name="Custom 3" value=""/>'
    '<customfield name="Custom 4" value=""/>'
    '<customfield name="Custom 5" value=""/>'
    '<build version="20121121" build_id="79970" submitter="Veracode" platform="Not Specified" lifecycle_stage="Not Specified" results_ready="true" '
    'policy_name="Veracode Transitional High" policy_version="1" policy_compliance_status="Did Not Pass" rules_status="Did Not Pass" '
    'grace_period_expired="false" scan_overdue="false">'
    '<analysis_unit analysis_type="Manual" published_date="2012-11-21T09:47:45-05:00" published_date_sec="1353509265" status="Results Ready"/>'
    '</build></application></applicationbuilds>')

mock_app_info_xml = ()

mock_app_list_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<applist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/applist" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/applist https://analysiscenter.veracode.com/resource/2.0/applist.xsd" account_id="00001">'
    '<app app_id="00001" app_name="TestApp"/>'
    '<app app_id="00002" app_name="TestApp2"/>'
    '</applist>')

mock_build_info_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<buildinfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/4.0/buildinfo" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/4.0/buildinfo https://analysiscenter.veracode.com/resource/4.0/buildinfo.xsd" '
    'account_id="00001" app_id="00001" build_id="00001"> '
    '<build version="TestApp 7.5.0.234" build_id="00001" submitter="Continuous Quality" platform="Not Specified" '
    'lifecycle_stage="Not Specified" results_ready="true" policy_name="Veracode Transitional Medium" policy_version="1" '
    'policy_compliance_status="Pass" rules_status="Pass" grace_period_expired="false" scan_overdue="false"> '
    '<analysis_unit analysis_type="Static" published_date="2013-02-14T12:39:53-05:00" published_date_sec="1360863593" '
    'status="Results Ready"/> '
    '</build></buildinfo>')

mock_build_info_xml_create_build = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<buildinfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/4.0/buildinfo" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/4.0/buildinfo https://analysiscenter.veracode.com/resource/4.0/buildinfo.xsd" '
    'account_id="00001" app_id="00001" build_id="00001"> '
    '<build version="TestCreateBuild" build_id="00002" submitter="Continuous Quality" platform="Not Specified" '
    'lifecycle_stage="Not Specified" results_ready="true" policy_name="Veracode Transitional Medium" policy_version="1" '
    'policy_compliance_status="Pass" rules_status="Pass" grace_period_expired="false" scan_overdue="false"> '
    '<analysis_unit analysis_type="Static" published_date="2013-02-14T12:39:53-05:00" published_date_sec="1360863593" '
    'status="Results Ready"/> '
    '</build></buildinfo>')

mock_build_info_xml_prescan_success = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<buildinfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/4.0/buildinfo" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/4.0/buildinfo https://analysiscenter.veracode.com/resource/4.0/buildinfo.xsd" '
    'account_id="00001" app_id="00001" build_id="00001"> '
    '<build version="TestApp 7.5.0.234" build_id="00001" submitter="Continuous Quality" platform="Not Specified" '
    'lifecycle_stage="Not Specified" results_ready="true" policy_name="Veracode Transitional Medium" policy_version="1" '
    'policy_compliance_status="Pass" rules_status="Pass" grace_period_expired="false" scan_overdue="false"> '
    '<analysis_unit analysis_type="Static" published_date="2013-02-14T12:39:53-05:00" published_date_sec="1360863593" '
    'status="Pre-Scan Success"/> '
    '</build></buildinfo>')

mock_build_info_xml_prescan_in_progress = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<buildinfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/4.0/buildinfo" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/4.0/buildinfo https://analysiscenter.veracode.com/resource/4.0/buildinfo.xsd" '
    'account_id="00001" app_id="00001" build_id="00001"> '
    '<build version="TestApp 7.5.0.234" build_id="00001" submitter="Continuous Quality" platform="Not Specified" '
    'lifecycle_stage="Not Specified" results_ready="true" policy_name="Veracode Transitional Medium" policy_version="1" '
    'policy_compliance_status="Pass" rules_status="Pass" grace_period_expired="false" scan_overdue="false"> '
    '<analysis_unit analysis_type="Static" published_date="2013-02-14T12:39:53-05:00" published_date_sec="1360863593" '
    'status="Pre-Scan In Progress"/> '
    '</build></buildinfo>')

mock_build_list_xml = (
    '<buildlist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/buildlist" xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/buildlist https://analysiscenter.veracode.com/resource/2.0/buildlist.xsd" account_id="00001" app_id="00001" app_name="testApp">'
    '<build build_id="00001" version="TestApp 7.5.0.234"/>'
    '<build build_id="00002" version="TestCreateBuild"/>'
    '</buildlist>')

mock_build_list_xml_create_build = (
    '<buildlist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/buildlist" xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/buildlist https://analysiscenter.veracode.com/resource/2.0/buildlist.xsd" account_id="00001" app_id="00001" app_name="testApp">'
    '<build build_id="00001" version="TestApp 7.5.0.234"/>'
    '</buildlist>')

mock_call_stacks_xml = ()

mock_error_xml = (
    '<error></error>')

mock_file_list = (
    ["TestFile01.jsp", "TestFile02.jsp", "TestFile03.class", "TestFile04.jsp",
    "TestFile05.htm", "TestFile06.class", "TestFile07.jsp", "TestFile08.jspi", "TestFile09.jsp"])

mock_file_list_blacklist = (
    ["TestFile03.class", "TestFile05.htm", "TestFile06.class", "TestFile08.jspi"])

mock_file_list_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<filelist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/filelist" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/filelist https://analysiscenter.veracode.com/resource/2.0/filelist.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '<file file_id="21271739" file_name="TestFile01.jsp" file_status="Uploaded"/>'
    '<file file_id="21243504" file_name="TestFile02.jsp" file_status="Uploaded"/>'
    '<file file_id="21243519" file_name="TestFile03.class" file_status="Uploaded"/>'
    '<file file_id="21243523" file_name="TestFile04.jsp" file_status="Uploaded"/>'
    '<file file_id="21243525" file_name="TestFile05.htm" file_status="Uploaded"/>'
    '<file file_id="21243527" file_name="TestFile06.class" file_status="Uploaded"/>'
    '<file file_id="21265337" file_name="TestFile07.jsp" file_status="Uploaded"/>'
    '<file file_id="21265341" file_name="TestFile08.jspi" file_status="Uploaded"/>'
    '<file file_id="21265343" file_name="TestFile09.jsp" file_status="Uploaded"/>'
    '</filelist>')

mock_file_list_blacklist_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<filelist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/filelist" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/filelist https://analysiscenter.veracode.com/resource/2.0/filelist.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '<file file_id="21243519" file_name="TestFile03.class" file_status="Uploaded"/>'
    '<file file_id="21243525" file_name="TestFile05.htm" file_status="Uploaded"/>'
    '<file file_id="21243527" file_name="TestFile06.class" file_status="Uploaded"/>'
    '<file file_id="21265341" file_name="TestFile08.jspi" file_status="Uploaded"/>'
    '</filelist>')

mock_file_list_remove_file_by_name_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<filelist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/filelist" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/filelist https://analysiscenter.veracode.com/resource/2.0/filelist.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '<file file_id="21271739" file_name="TestFile01.jsp" file_status="Uploaded"/>'
    '<file file_id="21243504" file_name="TestFile02.jsp" file_status="Uploaded"/>'
    '<file file_id="21243519" file_name="TestFile03.class" file_status="Uploaded"/>'
    '<file file_id="21243523" file_name="TestFile04.jsp" file_status="Uploaded"/>'
    '<file file_id="21243525" file_name="TestFile05.htm" file_status="Uploaded"/>'
    '<file file_id="21243527" file_name="TestFile06.class" file_status="Uploaded"/>'
    '<file file_id="21265337" file_name="TestFile07.jsp" file_status="Uploaded"/>'
    '<file file_id="21265341" file_name="TestFile08.jspi" file_status="Uploaded"/>'
    '</filelist>')

mock_file_list_empty_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<filelist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/filelist" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/filelist https://analysiscenter.veracode.com/resource/2.0/filelist.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '</filelist>')

mock_module_list = [{'module_id': '00000059', 'module_name': 'PrescanTest01.class'},
                    {'module_id': '00000060', 'module_name': 'PrescanTest02.class'},
                    {'module_id': '00000061', 'module_name': 'PrescanTest03.class'}]

mock_module_white_list = [{'module_id': '00000060', 'module_name': 'PrescanTest02.class'},
                          {'module_id': '00000061', 'module_name': 'PrescanTest03.class'}]

mock_policy_list_xml = ()

mock_prescan_results_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<prescanresults xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/prescanresults" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/prescanresults https://analysiscenter.veracode.com/resource/2.0/prescanresults.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '<module id="00000059" name="PrescanTest01.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="4KB" '
    'status="Missing Supporting Files - 1 File, Unsupported Framework - 1 File" has_fatal_errors="false">'
    '<issue details="Unsupported framework: Apache Axis"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest01Dependency01" details="Not Found (Optional)"/>'
    '</module>'
    '<module id="00000060" name="PrescanTest02.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="5KB" '
    'status="Missing Supporting Files - 2 Files, Unsupported Framework - 1 File" has_fatal_errors="false">'
    '<issue details="Unsupported framework: Apache Axis"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest02Dependency01" details="Not Found (Optional)"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest02Dependency02" details="Not Found (Optional)"/>'
    '</module>'
    '<module id="00000061" name="PrescanTest03.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="2KB" '
    'status="Missing Supporting Files - 2 Files" has_fatal_errors="false">'
    '<file_issue filename="com.mock.cmp.product.adhoc.PrescanTest03Dependency01" details="Not Found (Optional)"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest03Dependency02" details="Not Found (Optional)"/>'
    '</module></prescanresults>')

mock_prescan_results_xml_all_fatal_errors = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<prescanresults xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/prescanresults" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/prescanresults https://analysiscenter.veracode.com/resource/2.0/prescanresults.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '<module id="00000059" name="PrescanTest01.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="4KB" '
    'status="Missing Supporting Files - 1 File, Unsupported Framework - 1 File" has_fatal_errors="true">'
    '<issue details="Unsupported framework: Apache Axis"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest01Dependency01" details="Not Found (Optional)"/>'
    '</module>'
    '<module id="00000060" name="PrescanTest02.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="5KB" '
    'status="Missing Supporting Files - 2 Files, Unsupported Framework - 1 File" has_fatal_errors="true">'
    '<issue details="Unsupported framework: Apache Axis"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest02Dependency01" details="Not Found (Optional)"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest02Dependency02" details="Not Found (Optional)"/>'
    '</module>'
    '<module id="00000061" name="PrescanTest03.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="2KB" '
    'status="Missing Supporting Files - 2 Files" has_fatal_errors="true">'
    '<file_issue filename="com.mock.cmp.product.adhoc.PrescanTest03Dependency01" details="Not Found (Optional)"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest03Dependency02" details="Not Found (Optional)"/>'
    '</module></prescanresults>')

mock_prescan_results_xml_mixed = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<prescanresults xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://analysiscenter.veracode.com/schema/2.0/prescanresults" '
    'xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/prescanresults https://analysiscenter.veracode.com/resource/2.0/prescanresults.xsd" '
    'account_id="00001" app_id="00001" build_id="00002">'
    '<module id="00000059" name="PrescanTest01.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="4KB" '
    'status="Missing Supporting Files - 1 File, Unsupported Framework - 1 File" has_fatal_errors="false">'
    '<issue details="Unsupported framework: Apache Axis"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest01Dependency01" details="Not Found (Optional)"/>'
    '</module>'
    '<module id="00000060" name="PrescanTest02.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="5KB" '
    'status="Missing Supporting Files - 2 Files, Unsupported Framework - 1 File" has_fatal_errors="true">'
    '<issue details="Unsupported framework: Apache Axis"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest02Dependency01" details="Not Found (Optional)"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest02Dependency02" details="Not Found (Optional)"/>'
    '</module>'
    '<module id="00000061" name="PrescanTest03.class" platform="JVM / Java J2SE 6 / JAVAC_6" size="2KB" '
    'status="Missing Supporting Files - 2 Files" has_fatal_errors="true">'
    '<file_issue filename="com.mock.cmp.product.adhoc.PrescanTest03Dependency01" details="Not Found (Optional)"/>'
    '<file_issue filename="com.mock.ws.common.v1.PrescanTest03Dependency02" details="Not Found (Optional)"/>'
    '</module></prescanresults>')

mock_detailed_report_pdf = (b'')

mock_detailed_report_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<detailedreport xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://www.veracode.com/schema/reports/export/1.0" '
    'xsi:schemaLocation="https://www.veracode.com/schema/reports/export/1.0 https://analysiscenter.veracode.com/resource/detailedreport.xsd" '
    'report_format_version="1.1" app_name="testApp" app_id="00001" first_build_submitted_date="2012-12-20 22:24:36 UTC" '
    'version="1.0.1.0" build_id="00002" submitter="Continuous Quality" platform="Not Specified" '
    'assurance_level="3" business_criticality="3" generation_date="2013-02-20 20:01:33 UTC" veracode_level="VL3" '
    'total_flaws="4" flaws_not_mitigated="4" teams="Quality" life_cycle_stage="Not Specified" '
    'planned_deployment_date="" last_update_time="2013-02-19 23:45:37 UTC" is_latest_build="true" policy_name="Veracode Transitional Medium" '
    'policy_version="1" policy_compliance_status="Pass" policy_rules_status="Pass" grace_period_expired="false" scan_overdue="false" '
    'any_type_scan_due="2013-02-19 23:45:33 UTC" business_owner="Testing" business_unit="Not Specified" tags="App,Automation,CQ,Quality,Test">'
    '<static-analysis rating="A" score="98" submitted_date="2013-02-19 23:27:07 UTC" published_date="2013-02-19 23:45:33 UTC" '
    'analysis_size_bytes="330970">'
    '<modules>'
    '<module name="ActivityLogHelper.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="00001" score="99" '
    'numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="2" numflawssev4="0" numflawssev5="0"/>'
    '<module name="AccessFilter.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="0002" score="99" '
    'numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="1" numflawssev4="0" numflawssev5="0"/>'
    '<module name="JobRunner.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="00003" score="99" '
    'numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="1" numflawssev4="0" numflawssev5="0"/>'
    '<module name="EntityTypeHelper.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="12545" '
    'score="100" numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="0" numflawssev4="0" numflawssev5="0"/>'
    '<module name="IntegrationCodeSearchCriteria.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" '
    'loc="00004" score="100" numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="0" numflawssev4="0" numflawssev5="0"/>'
    '</modules>'
    '</static-analysis>'
    '<severity level="5"/>'
    '<severity level="4"/>'
    '<severity level="3">'
    '<category categoryid="21" categoryname="CRLF Injection" pcirelated="true">'
    '<desc>'
    '<para text="The acronym CRLF stands for &quot;Carriage Return, Line Feed&quot; and refers to the sequence of characters "'
    '"used to denote the end of a line of text.  CRLF injection vulnerabilities occur when data enters an application from an untrusted "'
    '"source and is not properly validated before being used.  For example, if an attacker is able to inject a CRLF into a log file, he "'
    '"could append falsified log entries, thereby misleading administrators or cover traces of the attack.  If an attacker is able to inject "'
    '"CRLFs into an HTTP response header, he can use this ability to carry out other attacks such as cache poisoning.  CRLF vulnerabilities "'
    '"primarily affect data integrity.  "/>'
    '</desc>'
    '<recommendations>'
    '<para text="Apply robust input filtering for all user-supplied data, using centralized data validation routines when possible.  "'
    '"Use output filters to sanitize all output derived from user-supplied input, replacing non-alphanumeric characters with their HTML entity equivalents."/>'
    '</recommendations></category></severity>'
    '<severity level="2"/>'
    '<severity level="1"/>'
    '<severity level="0"/>'
    '<flaw-status new="4" reopen="0" open="0" fixed="0" total="4" not_mitigated="4" sev-1-change="0" sev-2-change="0" sev-3-change="4" sev-4-change="0" sev-5-change="0"/>'
    '</detailedreport>')

mock_summary_report_pdf = (b'')

mock_summary_report_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<summaryreport xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="https://www.veracode.com/schema/reports/export/1.0" '
    'xsi:schemaLocation="https://www.veracode.com/schema/reports/export/1.0 https://analysiscenter.veracode.com/resource/summaryreport.xsd" '
    'report_format_version="1.1" app_name="testApp" app_id="00001" first_build_submitted_date="2012-12-20 22:24:36 UTC" '
    'version="1.0.1.0" build_id="00002" submitter="Continuous Quality" platform="Not Specified" assurance_level="3" '
    'business_criticality="3" generation_date="2013-02-20 19:24:37 UTC" veracode_level="VL3" total_flaws="4" flaws_not_mitigated="4" '
    'teams="Quality" life_cycle_stage="Not Specified" planned_deployment_date="" last_update_time="2013-02-19 23:45:37 UTC" '
    'is_latest_build="true" policy_name="Veracode Transitional Medium" policy_version="1" policy_compliance_status="Pass" '
    'policy_rules_status="Pass" grace_period_expired="false" scan_overdue="false" any_type_scan_due="2013-02-19 23:45:33 UTC" '
    'business_owner="Testing" business_unit="Not Specified" tags="App,Automation,CQ,Quality,Test">'
    '<static-analysis rating="A" score="98" submitted_date="2013-02-19 23:27:07 UTC" published_date="2013-02-19 23:45:33 UTC" analysis_size_bytes="0">'
    '<modules>'
    '<module name="ActivityLogHelper.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="00001" score="99" '
    'numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="2" numflawssev4="0" numflawssev5="0"/>'
    '<module name="AccessFilter.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="0002" score="99" '
    'numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="1" numflawssev4="0" numflawssev5="0"/>'
    '<module name="JobRunner.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="00003" score="99" '
    'numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="1" numflawssev4="0" numflawssev5="0"/>'
    '<module name="EntityTypeHelper.class" compiler="JAVAC_6" os="Java J2SE 6" architecture="JVM" loc="12545" '
    'score="100" numflawssev0="0" numflawssev1="0" numflawssev2="0" numflawssev3="0" numflawssev4="0" numflawssev5="0"/>'
    '</modules>'
    '</static-analysis>'
    '<severity level="5"/><severity level="4"/><severity level="3"><category categoryname="CRLF Injection" '
    'severity="Medium" count="2"/><category categoryname="Code Quality" severity="Medium" count="1"/><category '
    'categoryname="Session Fixation" severity="Medium" count="1"/></severity><severity level="2"/><severity level="1"/>'
    '<severity level="0"/><flaw-status new="4" reopen="0" open="0" fixed="0" total="4" not_mitigated="4" sev-1-change="0" '
    'sev-2-change="0" sev-3-change="4" sev-4-change="0" sev-5-change="0"/></summaryreport>')

mock_third_party_report_xml = ()

mock_third_party_report_pdf = (b'')

mock_update_build_xml = ()

mock_vendor_list_xml = ()


class TestVeracode():

    test_instance = None

    @classmethod
    def setup_class(cls):
        cls.test_instance = AbstractAPI("myTestUsername", "myTestPassword")

    @classmethod
    def teardown_class(cls):
        cls.test_instance = None

    def test_begin_prescan(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_build_info_xml
            mock_method.return_value = r
            begin_prescan_xml = self.test_instance.begin_prescan(34, 52)
            assert begin_prescan_xml == mock_build_info_xml

    def test_begin_scan(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_build_info_xml
            mock_method.return_value = r
            begin_scan_xml = self.test_instance.begin_scan(34, ["something", "something1", "something2"], False)
            assert begin_scan_xml == mock_build_info_xml

    def test_create_app(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_info_xml
            mock_method.return_value = r
            create_app_xml = self.test_instance.create_app(
                "myApp", "High", "This is an app description.", 11, "testPolicy", "testBusinessUnit", "testBusinessOwner",
                "testBusinessOwnerEmail@example.com", "testTeam", "testOrigin", "testIndustry", "testAppType", "testDeploymentType",
                "testWebApplication", "testArcherAppName", "testTags")
            assert create_app_xml == mock_app_info_xml

    def test_create_build(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_build_info_xml
            mock_method.return_value = r
            create_build_xml = self.test_instance.create_build(34, "testVersion", "testLifecycleStage", 19, "2013-22-01")
            assert create_build_xml == mock_build_info_xml

    def test_delete_app(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_list_xml
            mock_method.return_value = r
            delete_app_xml = self.test_instance.delete_app(34)
            assert delete_app_xml == mock_app_list_xml

    def test_delete_build(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_list_xml
            mock_method.return_value = r
            delete_build_xml = self.test_instance.delete_build(34)
            assert delete_build_xml == mock_app_list_xml

    def test_detailed_report_pdf(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.content = mock_detailed_report_pdf
            mock_method.return_value = r
            detailed_report_pdf = self.test_instance.detailed_report_pdf(52)
            assert detailed_report_pdf == mock_detailed_report_pdf

    def test_get_app_builds(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_builds_xml
            mock_method.return_value = r
            app_builds_xml = self.test_instance.get_app_builds()
            assert app_builds_xml == mock_app_builds_xml

    def test_get_app_info(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_info_xml
            mock_method.return_value = r
            app_info_xml = self.test_instance.get_app_info(52)
            assert app_info_xml == mock_app_info_xml

    def test_get_app_list(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_list_xml
            mock_method.return_value = r
            app_list_xml = self.test_instance.get_app_list()
            assert app_list_xml == mock_app_list_xml

    def test_get_build_info(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_build_info_xml
            mock_method.return_value = r
            build_info_xml = self.test_instance.get_build_info(34, 52)
            assert build_info_xml == mock_build_info_xml

    def test_get_build_list(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_info_xml
            mock_method.return_value = r
            build_list_xml = self.test_instance.get_build_list(52)
            assert build_list_xml == mock_app_info_xml

    def test_get_call_stacks(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_call_stacks_xml
            mock_method.return_value = r
            call_stacks_xml = self.test_instance.get_call_stacks(34, 975)
            assert call_stacks_xml == mock_call_stacks_xml

    def test_get_file_list(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_file_list_xml
            mock_method.return_value = r
            file_list_xml = self.test_instance.get_file_list(34, 52)
            assert file_list_xml == mock_file_list_xml

    def test_get_policy_list(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_policy_list_xml
            mock_method.return_value = r
            policy_list_xml = self.test_instance.get_policy_list()
            assert policy_list_xml == mock_policy_list_xml

    def test_get_prescan_results(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_prescan_results_xml
            mock_method.return_value = r
            prescan_results_xml = self.test_instance.get_prescan_results(34, 52)
            assert prescan_results_xml == mock_prescan_results_xml

    def test_get_vendor_list(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_vendor_list_xml
            mock_method.return_value = r
            vendor_list_xml = self.test_instance.get_vendor_list()
            assert vendor_list_xml == mock_vendor_list_xml

    def test_remove_file(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_file_list_xml
            mock_method.return_value = r
            remove_file_xml = self.test_instance.remove_file(34, 3420)
            assert remove_file_xml == mock_file_list_xml

    def test_third_party_report_pdf(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.content = mock_third_party_report_pdf
            mock_method.return_value = r
            third_party_report_pdf = self.test_instance.third_party_report_pdf(52)
            assert third_party_report_pdf == mock_third_party_report_pdf

    def test_summary_report_pdf(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.content = mock_summary_report_pdf
            mock_method.return_value = r
            summary_report_pdf = self.test_instance.summary_report_pdf(52)
            assert summary_report_pdf == mock_summary_report_pdf

    def test_upload_file(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_file_list_xml
            mock_method.return_value = r
            fileName = "myUploadFile.txt"
            with open(fileName, "w+") as f:
                f.write("test")
            upload_file_xml = self.test_instance.upload_file(34, fileName)
            os.remove(fileName)
            assert upload_file_xml == mock_file_list_xml

    def test_update_app(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_app_info_xml
            mock_method.return_value = r
            update_app_xml = self.test_instance.update_app(
                34, "myApp", "High", "testPolicy", "testBusinessUnit", "testBusinessOwner",
                "testBusinessOwnerEmail@example.com", "testTeam", "testOrigin", "testIndustry", "testAppType", "testDeploymentType",
                "testArcherAppName", "testTags", "testCustomFieldName", "testCustomFieldValue")
            assert update_app_xml == mock_app_info_xml

    def test_update_build(self):
        with patch.object(requests, "request") as mock_method:
            r = requests.Response
            r.text = mock_update_build_xml
            mock_method.return_value = r
            update_build_xml = self.test_instance.update_build(34, 52, "testVersion", "testLifecycleStage", "2013-22-01")
            assert update_build_xml == mock_update_build_xml


class TestAPI():

    test_instance = None

    @classmethod
    def setup_class(cls):
        with patch("lantern.AbstractAPI.get_app_list") as get_app_list:
            get_app_list.return_value = mock_app_list_xml
            with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
                get_build_info.return_value = mock_build_info_xml
                with patch("lantern.AbstractAPI.get_build_list") as get_build_list:
                    get_build_list.return_value = mock_build_list_xml
                    cls.test_instance = API("myTestUsername", "myTestPassword", "TestApp", "TestApp 7.5.0.234")

    @classmethod
    def teardown_class(cls):
        cls.test_instance = None

    def test_begin_prescan(self):
        with patch("lantern.AbstractAPI.begin_prescan") as begin_prescan:
                begin_prescan.return_value = mock_build_info_xml
                result = self.test_instance.begin_prescan()
                assert result == mock_build_info_xml

    def test_begin_scan(self):
        with patch("lantern.AbstractAPI.begin_scan") as begin_scan:
            begin_scan.return_value = mock_build_info_xml
            begin_scan_xml = self.test_instance.begin_scan(mock_prescan_results_xml, ["PrescanTest01.*"])
            assert begin_scan_xml == mock_build_info_xml

    def test_create_module_white_list(self):
        module_white_list = self.test_instance.create_module_white_list(mock_module_list, ["PrescanTest01.*"])
        assert module_white_list == mock_module_white_list

    def test_compare_file_list(self):
        with patch("lantern.AbstractAPI.get_file_list") as get_file_list:
            get_file_list.return_value = mock_file_list_blacklist_xml
            positive_result = self.test_instance.compare_file_list(os.getcwd() + "/ext/", ["*.jsp"])
            assert positive_result == []
            negative_result = self.test_instance.compare_file_list(os.getcwd(), ["*.jsp"])
            assert negative_result != []

    def test_compare_module_list(self):
        module_white_list = self.test_instance.compare_module_list(mock_prescan_results_xml, ["PrescanTest01.*"])
        assert module_white_list == mock_module_white_list

    def test_create_new_build(self):
        with patch("lantern.AbstractAPI.get_build_list") as get_build_list:
            get_build_list.return_value = mock_build_list_xml_create_build
            with patch("lantern.AbstractAPI.create_build") as create_build:
                create_build.return_value = mock_build_info_xml_create_build
                self.test_instance.set_build_id("TestCreateBuild")
                result = self.test_instance.build_id
                assert result == "00002"

    def test_use_existing_build(self):
        with patch("lantern.AbstractAPI.get_build_list") as get_build_list:
            get_build_list.return_value = mock_build_list_xml
            self.test_instance.set_build_id("TestCreateBuild")
            result = self.test_instance.build_id
            assert result == "00002"

    def test_delete_build(self):
        with patch("lantern.AbstractAPI.delete_build") as delete_build:
            delete_build.return_value = mock_app_list_xml
            result = self.test_instance.delete_build()
            assert result == mock_app_list_xml

    def test_detailed_report(self):
        with patch("lantern.AbstractAPI.detailed_report") as detailed_report:
            detailed_report.return_value = mock_detailed_report_xml
            with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
                get_build_info.return_value = mock_build_info_xml
                result = self.test_instance.detailed_report(4, 0.001, 0.001, 2)
                assert result == mock_detailed_report_xml

    def test_detailed_report_exceeds_retries(self):
        with patch("lantern.AbstractAPI.detailed_report") as detailed_report:
            detailed_report.return_value = mock_detailed_report_xml
            with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
                get_build_info.return_value = mock_build_info_xml_prescan_success
                with nose.tools.assert_raises(ExceededRetries):
                    self.test_instance.detailed_report(4, 0.001, 0.001, 2)

    def test_get_app_builds(self):
        with patch("lantern.AbstractAPI.get_app_builds") as get_app_builds:
            get_app_builds.return_value = mock_app_builds_xml
            result = self.test_instance.get_app_builds()
            assert result == mock_app_builds_xml

    def test_get_build_info_status(self):
        result = self.test_instance.get_build_info_status(mock_build_info_xml)
        assert result == "Results Ready"

    def test_get_build_version(self):
        result = self.test_instance.get_build_version(mock_build_info_xml)
        assert result == "TestApp 7.5.0.234"

    def test_get_module_list(self):
        module_list = self.test_instance.get_module_list(mock_prescan_results_xml)
        assert module_list == mock_module_list

    def test_get_prescan_results(self):
        with patch("lantern.AbstractAPI.get_prescan_results") as get_prescan_results:
            get_prescan_results.return_value = mock_prescan_results_xml
            with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
                get_build_info.return_value = mock_build_info_xml_prescan_success
                result = self.test_instance.get_prescan_results(1, 0, 0.001, 2)
            assert result == mock_prescan_results_xml

    def test_get_prescan_results_error_status_not_ready(self):
        with patch("lantern.AbstractAPI.get_prescan_results") as get_prescan_results:
            get_prescan_results.return_value = mock_prescan_results_xml
            with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
                get_build_info.return_value = mock_build_info_xml_prescan_in_progress
                with nose.tools.assert_raises(ExceededRetries):
                    self.test_instance.get_prescan_results(4, 0, 0.001, 2)

    def test_get_xml_attrib_error(self):
        with patch.object(API, 'get_xml_attrib') as mock:
            with nose.tools.assert_raises(ReceivedErrorXML):
                mock.side_effect = ReceivedErrorXML
                API.get_xml_attrib("<error>This is an error</error>")

    def test_poll_detailed_report(self):
        with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
            get_build_info.return_value = mock_build_info_xml
            with patch("lantern.AbstractAPI.detailed_report") as detailed_report:
                detailed_report.return_value = mock_detailed_report_xml
                result = self.test_instance.detailed_report(1, 0, 0.001, 2)
                assert result == mock_detailed_report_xml

    def test_poll_detailed_report_pdf(self):
        with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
            get_build_info.return_value = mock_build_info_xml
            with patch("lantern.AbstractAPI.detailed_report_pdf") as detailed_report_pdf:
                detailed_report_pdf.return_value = mock_detailed_report_pdf
                result = self.test_instance.detailed_report_pdf(1, 0, 0.001, 2)
                assert result == mock_detailed_report_pdf

    def test_poll_summary_report(self):
        with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
            get_build_info.return_value = mock_build_info_xml
            with patch("lantern.AbstractAPI.summary_report") as summary_report:
                summary_report.return_value = mock_summary_report_xml
                result = self.test_instance.summary_report(1, 0, 0.001, 2)
                assert result == mock_summary_report_xml

    def test_poll_summary_report_pdf(self):
        with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
            get_build_info.return_value = mock_build_info_xml
            with patch("lantern.AbstractAPI.summary_report_pdf") as summary_report_pdf:
                summary_report_pdf.return_value = mock_summary_report_pdf
                result = self.test_instance.summary_report_pdf(1, 0, 0.001, 2)
                assert result == mock_summary_report_pdf

    def test_poll_third_party_report_pdf(self):
        with patch("lantern.AbstractAPI.get_build_info") as get_build_info:
            get_build_info.return_value = mock_build_info_xml
            with patch("lantern.AbstractAPI.third_party_report_pdf") as third_party_report_pdf:
                third_party_report_pdf.return_value = mock_third_party_report_pdf
                result = self.test_instance.third_party_report_pdf(1, 0, 0.001, 2)
                assert result == mock_third_party_report_pdf

    def test_remove_file_by_name(self):
        with patch("lantern.AbstractAPI.get_file_list") as get_file_list:
            get_file_list.return_value = mock_file_list_xml
            with patch("lantern.AbstractAPI.remove_file") as remove_file:
                remove_file.return_value = mock_file_list_remove_file_by_name_xml
                file_list_remove_file_by_name_xml = self.test_instance.remove_file_by_name("TestFile09.jsp")
                assert file_list_remove_file_by_name_xml == mock_file_list_remove_file_by_name_xml
                nose.tools.assert_raises(FileNotFound, self.test_instance.remove_file_by_name, "foo.txt")

    def test_remove_file_retry(self):
        with patch("lantern.AbstractAPI.get_file_list") as get_file_list:
            get_file_list.return_value = mock_file_list_xml
            with patch("lantern.AbstractAPI.remove_file") as remove_file:
                remove_file.return_value = mock_file_list_empty_xml
                file_list_remove_file_retry_xml = self.test_instance.remove_file_retry()
                assert file_list_remove_file_retry_xml == mock_file_list_empty_xml

    def test_set_build_id_attribute_error(self):
        with patch.object(API, 'set_build_id') as mock:
            with nose.tools.assert_raises(AttributeError):
                mock.side_effect = AttributeError
                self.test_instance.set_build_id("this will cause a attribute error!")

    def test_upload_file_with_blacklist(self):
        with patch("lantern.AbstractAPI.upload_file") as upload_file:
            upload_file.return_value = mock_file_list_blacklist_xml
            with patch("lantern.AbstractAPI.get_file_list") as get_file_list:
                get_file_list.return_value = mock_file_list_empty_xml
                file_list_upload_file_xml = self.test_instance.upload_file(os.getcwd() + "/ext/", ["*.jsp"])
                assert file_list_upload_file_xml == mock_file_list_blacklist_xml

    def test_xml_attrib_for_error_xml(self):
        with nose.tools.assert_raises(ReceivedErrorXML):
            self.test_instance.get_build_info_status(mock_error_xml)
