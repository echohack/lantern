import sys
import os
import lantern

def write_text_results(data, outfilename, encoding="utf-8"):
    with open(outfilename, "w") as f:
        f.write(data)
        print("Data written to {0}.".format(outfilename))


username = os.environ['veracode_user']
password = os.environ['veracode_password']
app_name =  os.environ['veracode_app_name']
binaries_dir = os.environ['workspace']+ '/output/static_security_build'
build_name = os.environ['BUILD_NUMBER']
local_scan_delay = 60

global_black_list = [
    '*.[Ii]nstall*', '*.*manifest*', '*.sql*', '*Test*.*', '*.asax', '*.asmx', '*.aspx', '*.browser', '*.chm',
    '*.[Cc]onfig*', '*.cs', '*.css', '*.cmd', '*.cshtml', '*.dacpac', '*.dbschema', '*.deployment', '*.dgml',
    '*.DS_Store', '*.eot', '*.fakesconfig', '*.fs', '*.gif', '*.htm*', '*.ico', '*.ini', '*.js', '*.json',
    '*.lastcodeanalysissucceeded', '*.less', '*.MARKDOWN', '*.map', '*.md', '*.mht', '*.ndoc', '*.nupkg', '*.nuspec',
    '*.otf', '*.pfx', '*.png', '*.ps1', '*.resx', '*.sitemap', '*.sh', '*.sqp', '*.svc', '*.svg', '*.targets', '*.ttf',
    '*.txt', '*.vsto', '*.xml', '*.xlsx', '*.xsd', '*.xsl', '*.woff', 'Antlr*','AxInterop.*', 'C1.*', 'Castle.Core.*',
    'com.contoso.*', 'com.google.*', 'com.sshtool.*', 'CommonBE.*', 'CrystalDecisions.*', 'CuteEditor.*',
    'DevExpress.*', 'DocumentFormat.*', 'FluentNHibernate.*', 'kodo.*', 'Infragistics2.*', 'Interop.*', 'Ionic.Zip.*',
    'log4net.*', 'Mabry.*', '[Mm]icrosoft.*', '*.Moles.dll', 'net.sf.jmimemagic.*', 'org.apache.*', 'org.drools.*',
    'org.jboss.*', 'org.springframework.*', 'PolicyBE.*', 'StructureMap.*', '[Ss]ystem.*', 'Telerik*', 'WSAPI*.dll',
    'Abyss.dll', 'AjaxControlToolkit.dll', 'AuthenticationInterfaces.dll', 'BackgroundCopyManager.dll', 'bii.exe',
    'Coalesys.WebMenu.dll', 'EntityFramework.dll', 'ICSharpCode.SharpZipLib.dll', 'IRQuery.dll', 'jscoverage.exe',
    'LightLogger.dll', 'Moq.dll', 'NetSpell.SpellChecker.dll', 'nunit.*', 'Office.dll', 'ojdbc6-*.jar',
    'ONSMessages.dll', 'PublicDomain.dll', 'QASupport.dll', 'Rhino.Mocks.dll', 'RouteDebug.dll', 'SEAREACH4.DLL',
    'ServiceStack.Text.dll', 'SourceSafeTypeLib.dll', 'SqlPackage.exe', 'stdole.dll', 'TallComponents.PDF.Layout.dll',
    'WebDriver.dll', 'weblogic.*', 'Xceed*', 'XPCommonControls.dll']

v = lantern.API(username, password, app_name, build_name)
v.upload_file_retry(binaries_dir, global_black_list)
v.begin_prescan(v.app_id, v.build_id, auto_scan=True)
prescan_results_filename = "{0}-PrescanResults-{1}.xml".format(app_name, build_name)
# try getting the prescan results. Poll the Veracode service with an exponential backoff until we get results or until it fails.
prescan_results_xml = v.get_prescan_results(10, 0, 60, 2)  # max wait time = 34.1 hours + local_scan_delay
write_text_results(prescan_results_xml, prescan_results_filename)
