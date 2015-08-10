"""
This example script is a full example of how lantern can be used when
running behind a Jenkins job.
"""

import sys
import os
# jenkins exposes the workspace directory through env.
sys.path.append(os.environ['WORKSPACE'])
import lantern

# env variables are job parameters in the Jenkins job.
username = os.environ['VERACODE_USERNAME']
password = os.environ['VERACODE_PASSWORD']
app_name = os.environ['VERACODE_APP_NAME']
binaries_dir = os.environ['VERACODE_BINARIES_DIR']
build_name = os.environ['VERACODE_BUILD_NAME']
local_black_list = os.environ['VERACODE_BLACK_LIST'].split(",")
local_scan_delay = int(os.environ['VERACODE_SCAN_DELAY'])


def write_text_results(data, outfilename, encoding="utf-8"):
    with open(outfilename, "w") as f:
        f.write(data)
        print("Data written to {0}.".format(outfilename))


def write_binary_results(data, outfilename):
    with open(outfilename, "wb") as f:
        f.write(data)
        print("Data written to {0}.".format(outfilename))

"""
A hard-coded list of third party files that we never want to upload to the Veracode service.
The list can take glob pattern matching.
Extremely useful for reducing long scan times.
"""
global_black_list = ["*.[Ii]nstall*", "*.*manifest*", "*.sql*", "*Test*.*", "*.chm", "*.config*", "*.cs", "*.dacpac", "*.dbschema", "*.deployment", "*.dgml", "*.fakesconfig", "*.fs", "*.ini", "*.lastcodeanalysissucceeded", "*.mht", "*.ndoc", "*.resx", "*.sh", "*.sqp", "*.targets", "*.txt", "*.vsto", "*.xml", "*.xlsx", "*.xsd", "Antlr3.*", "AxInterop.*", "C1.*", "Castle.Core.*", "com.contoso.*", "com.google.*", "com.sshtool.*", "CommonBE.*", "CrystalDecisions.*", "CuteEditor.*", "DevExpress.*", "DocumentFormat.*", "FluentNHibernate.*", "kodo.*", "Infragistics2.*", "Interop.*", "Ionic.Zip.*", "log4net.*", "Mabry.*", "[Mm]icrosoft.*", "*.Moles.dll", "net.sf.jmimemagic.*", "org.apache.*", "org.drools.*", "org.jboss.*", "org.springframework.*", "PolicyBE.*", "StructureMap.*", "[Ss]ystem.*", "Telerik*", "WSAPI*.dll", "Abyss.dll", "AjaxControlToolkit.dll", "AuthenticationInterfaces.dll", "BackgroundCopyManager.dll", "bii.exe", "Coalesys.WebMenu.dll", "EntityFramework.dll", "ICSharpCode.SharpZipLib.dll", "IRQuery.dll", "jscoverage.exe", "LightLogger.dll", "Moq.dll", "NetSpell.SpellChecker.dll", "nunit.*", "Office.dll", "ojdbc6-*.jar", "ONSMessages.dll", "PublicDomain.dll", "QASupport.dll", "Rhino.Mocks.dll", "RouteDebug.dll", "SEAREACH4.DLL", "ServiceStack.Text.dll", "SourceSafeTypeLib.dll", "SqlPackage.exe", "stdole.dll", "TallComponents.PDF.Layout.dll", "VIM.Shared.dll", "WebDriver.dll", "weblogic.*", "Xceed*", "XPCommonControls.dll"]

for item in local_black_list:
    global_black_list.append(item)

# Output to stdout so we can debug failures via Jenkins console.
print("Application Name: {},\rBuild Name: {},\rBinaries Directory: {},\rLocal Black List: {},\rAll Black List Patterns: {},\rLocal Scan Delay: {}".format(app_name, build_name, binaries_dir, local_black_list, global_black_list, local_scan_delay))

# instanciate lantern
v = lantern.API(username, password, app_name, build_name)

# upload the files to Veracode
v.upload_file_retry(binaries_dir, global_black_list)

# set the prescan results filename
prescan_results_filename = "{0}-PrescanResults-{1}.xml".format(app_name, build_name)

# start the prescan
v.begin_prescan(v.app_id, v.build_id)

# try getting the results. Poll the Veracode service with an exponential backoff until we get results or until it fails.
prescan_results_xml = v.get_prescan_results(10, 0, 60, 2)  # max wait time = 34.1 hours + local_scan_delay
print(prescan_results_xml)

# save the prescan results when uploading files is done.
write_text_results(prescan_results_xml, prescan_results_filename)

# start the scan
begin_scan_xml = v.begin_scan(prescan_results_xml, global_black_list)
print(begin_scan_xml)

# set the scan result report file names.
detailed_report_xml_name = "{0}-DetailedReport-{1}.xml".format(app_name, build_name)
detailed_report_pdf_name = "{0}-DetailedReportPDF-{1}.pdf".format(app_name, build_name)
summary_report_xml_name = "{0}-SummaryReport-{1}.xml".format(app_name, build_name)
summary_report_pdf_name = "{0}-SummaryReportPDF-{1}.pdf".format(app_name, build_name)

"""
try getting the scan results. Poll the Veracode service with an exponential backoff until we get results or until it fails.
Note that only the first result needs to wait, since the rest of the results should be available when the first one is ready.
"""
write_text_results(v.detailed_report(10000, local_scan_delay, 60, 2), detailed_report_xml_name)
write_text_results(v.summary_report(), summary_report_xml_name)
write_binary_results(v.detailed_report_pdf(), detailed_report_pdf_name)
write_binary_results(v.summary_report_pdf(), summary_report_pdf_name)
