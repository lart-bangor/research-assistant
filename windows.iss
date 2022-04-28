; INNO SETUP Script for the LART Research Client
; Normally this script will be run automatically from `manage.py build`.

#define MyAppName "Research Client"
#define MyAppVersion "0.1a2"
#define MyAppPublisherShort "LART"
#define MyAppPublisher "Bangor University Language Attitudes Research Team"
#define MyAppURL "https://github.com/lart-bangor"
#define MyAppPlatformString "windows_amd64"
#define MyAppDevDir "C:\Users\flb22gyt\Development\lart-research-client"
#define MyAppExeName MyAppName + ".exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications. This is a GUID/UUID.
AppId={{FB4E28E2-1A37-4FC5-8C44-D63D3672EA65}
AppName={#MyAppPublisherShort} {#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppPublisherShort} {#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2022 {#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppPublisherShort}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile={#MyAppDevDir}\LICENSE
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#MyAppDevDir}\build\pyinstaller\dist
OutputBaseFilename={#MyAppPublisherShort} {#MyAppName}.{#MyAppPlatformString}
SetupIconFile={#MyAppDevDir}\lart_research_client\web\img\appicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
#if "windows_amd64" == MyAppPlatformString
    ArchitecturesAllowed=x64
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyAppDevDir}\build\pyinstaller\dist\Research Client.windows_amd64\Research Client\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppDevDir}\build\pyinstaller\dist\Research Client.windows_amd64\Research Client\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppPublisherShort} {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppPublisherShort} {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppPublisherShort} {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
