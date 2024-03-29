﻿; INNO SETUP Script for the LART Research Assistant
; Normally this script will be run automatically from `manage.py build`.

#define MyAppName "[[APP_NAME]]"
#define MyAppVersion "[[APP_VERSION]]"
#define MyAppAuthor "[[APP_AUTHOR]]"
#define MyAppLongAuthor "[[APP_LONG_AUTHOR]]"
#define MySafeAppName "[[SAFE_APP_NAME]]"
#define MySafeAppVersion "[[SAFE_APP_VERSION]]"
#define MySafeAppAuthor "[[SAFE_APP_AUTHOR]]"
#define MySafeAppLongAuthor "[[SAFE_APP_LONG_AUTHOR]]"
#define MyAppURL "[[APP_URL]]"
#define MyAppPlatformString "[[PLATFORM_STRING]]"
#define MyAppDevDir "[[WORKSPACE_PATH]]"
#define MyAppDistributableName MySafeAppAuthor + "_" + MySafeAppName + "_v" + MySafeAppVersion + "-"  + MyAppPlatformString
#define MyAppExeName MySafeAppName + ".exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications. This is a GUID/UUID.
AppId={{FB4E28E2-1A37-4FC5-8C44-D63D3672EA65}
AppName={#MyAppAuthor} {#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppAuthor} {#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppLongAuthor}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2022 {#MyAppLongAuthor}
DefaultDirName={autopf}\{#MySafeAppAuthor}\{#MySafeAppName}
DisableProgramGroupPage=yes
LicenseFile={#MyAppDevDir}\LICENSE.AGPL-3.0
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#MyAppDevDir}\build\{#MyAppPlatformString}\pyinstaller\dist
OutputBaseFilename={#MyAppDistributableName}
OutputManifestFile={#MyAppDistributableName}.manifest
SetupIconFile={#MyAppDevDir}\research_assistant\web\img\setupicon.ico
UninstallDisplayIcon={#MyAppDevDir}\research_assistant\web\img\setupicon.ico
Compression=lzma
SolidCompression=yes
ShowLanguageDialog=auto
LanguageDetectionMethod=uilanguage
WizardStyle=modern
WizardSmallImageFile={#MyAppDevDir}\research_assistant\web\img\appicon.bmp
; These don't seem to have any effect with WizardStyle=modern
; BackColor=$FF0000
; BackColor2=$000000
; BackSolid=no
#if "win64" == MyAppPlatformString
    ArchitecturesAllowed=x64
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyAppDevDir}\build\{#MyAppPlatformString}\pyinstaller\dist\{#MyAppDistributableName}\{#MySafeAppName}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppDevDir}\build\{#MyAppPlatformString}\pyinstaller\dist\{#MyAppDistributableName}\{#MySafeAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppAuthor} {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppAuthor} {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppAuthor} {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Registry]
; App Paths shortcut to the app creates an alias without the need to add app dir to the PATH
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\lartrc.exe"; ValueType: string; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\lartrc.exe"; ValueName: "Path"; ValueType: string; ValueData: "{app}\"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "-c update"; StatusMsg: "Updating app settings..."; Flags: runasoriginaluser
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
