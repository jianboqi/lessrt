;This file will be executed next to the application bundle image
;I.e. current directory will contain folder LESS with application files
[Setup]
AppId={{fxApplication}}
AppName=LESS
AppVersion=1.8.6       
AppVerName=LESS 1.8.6
AppPublisher=Jianbo Qi
AppComments=LessGUI
AppCopyright=Copyright (C) 2018
;AppPublisherURL=http://java.com/
;AppSupportURL=http://java.com/
;AppUpdatesURL=http://java.com/
;DefaultDirName={localappdata}\LESS
DefaultDirName={localappdata}\LESS
DisableStartupPrompt=Yes
DisableDirPage=No
DisableProgramGroupPage=Yes
DisableReadyPage=Yes
DisableFinishedPage=Yes
DisableWelcomePage=Yes
DefaultGroupName=Jianbo Qi
;Optional License
LicenseFile=
;WinXP or above
MinVersion=0,5.1 
OutputBaseFilename=LESS-1.8.6
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=LESS\LESS.ico
UninstallDisplayIcon={app}\LESS.ico
UninstallDisplayName=LESS
WizardImageStretch=No
WizardSmallImageFile=LESS-setup-icon.bmp   
ArchitecturesInstallIn64BitMode=x64


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "LESS\LESS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LESS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LESS"; Filename: "{app}\LESS.exe"; IconFilename: "{app}\LESS.ico"; Check: returnTrue()
Name: "{commondesktop}\LESS"; Filename: "{app}\LESS.exe";  IconFilename: "{app}\LESS.ico"; Check: returnFalse()


[Run]
Filename: "{app}\app\bin\scripts\Lesspy\bin\rt\lessrt\VC_redist_2017.x64.exe";Parameters: "/install /norestart"; StatusMsg: "Installing VC++ redistributables..."; Check: VC2017RedistNeedsInstall ;Flags: waituntilterminated
Filename: "{app}\LESS.exe"; Parameters: "-Xappcds:generatecache"; Check: returnFalse()
Filename: "{app}\LESS.exe"; Description: "{cm:LaunchProgram,LESS}"; Flags: nowait postinstall skipifsilent; Check: returnTrue()
Filename: "{app}\LESS.exe"; Parameters: "-install -svcName ""LESS"" -svcDesc ""LESS"" -mainExe ""LESS.exe""  "; Check: returnFalse()

[UninstallRun]
Filename: "{app}\LESS.exe "; Parameters: "-uninstall -svcName LESS -stopOnUninstall"; Check: returnFalse()

[Code]
function returnTrue(): Boolean;
begin
  Result := True;
end;

function returnFalse(): Boolean;
begin
  Result := False;
end;

function InitializeSetup(): Boolean;
begin
// Possible future improvements:
//   if version less or same => just launch app
//   if upgrade => check if same app is running and wait for it to exit
//   Add pack200/unpack200 support? 
  Result := True;
end;

function VC2017RedistNeedsInstall(): Boolean;
var 
  Version: String;
begin
  if (RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version)) then
  begin
    // Is the installed version at least 14.14 ? 
    //Log('VC Redist Version check : found ' + Version);
    //Result := (CompareStr(Version, 'v14.14.26429.03')<0);
    Result := False;
  end
  else 
  begin
    // Not even an old version installed
    Result := True;
  end;
end;
