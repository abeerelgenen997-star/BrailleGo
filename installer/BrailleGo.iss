; ---------------------------------------------------------------------------
;  Braille Go — Inno Setup script (installer)
;
;  يبني مُثبِّتًا احترافيًا لواجهة wxPython بنسخة 64-بت:
;    - نسخ التطبيق إلى مجلد البرامج
;    - إنشاء اختصار في قائمة ابدأ وعلى سطح المكتب (اختياري)
;    - تسجيل التطبيق في "إضافة أو إزالة البرامج" مع ملف إزالة كامل
;    - تشغيل التطبيق بعد التثبيت (اختياري)
;
;  البناء (بعد إنتاج dist\BrailleGo.exe):
;    ISCC.exe /DAppVersion=1.3.0 installer\BrailleGo.iss
;
;  ملاحظة: المُثبِّت يعمل دون صلاحيات مسؤول افتراضيًا (يُثبّت للمستخدم
;  الحالي)، ويمكن للمستخدم اختيار التثبيت لكل المستخدمين من نافذة التثبيت.
; ---------------------------------------------------------------------------

#ifndef AppVersion
  #define AppVersion "1.3.0"
#endif
#ifndef SourceExe
  #define SourceExe "..\dist\BrailleGo.exe"
#endif

#define AppName "Braille Go"
#define AppNameAr "برايل جو"
#define AppPublisher "Braille Go Project"
#define AppURL "https://github.com/abeerelgenen997-star/BrailleGo"

[Setup]
AppId={{C62013F8-A5D8-49E9-BD60-70D2A30AB067}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}/releases/latest
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist\installer
OutputBaseFilename=BrailleGo-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\BrailleGo.exe
DisableWelcomePage=no
SetupLogging=yes
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "BrailleGo.exe"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "..\USER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ACCESSIBILITY.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\BrailleGo.exe"; Comment: "{#AppNameAr}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\BrailleGo.exe"; Comment: "{#AppNameAr}"; Tasks: desktopicon

[Run]
Filename: "{app}\BrailleGo.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
