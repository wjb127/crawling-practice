#define MyAppName "SmartCrawler Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CrawlTech Solutions"
#define MyAppURL "https://crawltech.solutions"
#define MyAppExeName "웹크롤러.exe"
#define MyAppDescription "고급 웹 크롤링 데스크탑 애플리케이션"

[Setup]
; 기본 설정
AppId={{A1B2C3D4-E5F6-7890-ABCD-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2025 {#MyAppPublisher}

; 설치 경로 설정
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; 출력 설정
OutputDir=installer
OutputBaseFilename=SmartCrawler_Pro_Setup_v{#MyAppVersion}
SetupIconFile=app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; 권한 설정
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 라이선스 및 정보 파일
LicenseFile=LICENSE.txt
InfoBeforeFile=README_INSTALL.txt
InfoAfterFile=INSTALLATION_COMPLETE.txt

; 언어 설정
ShowLanguageDialog=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 메인 실행 파일
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 문서 파일들
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "README.txt"
Source: "BUILD_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "BUILD_GUIDE.txt"
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; 라이선스 및 설치 안내
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_INSTALL.txt"; DestDir: "{app}"; Flags: ignoreversion

; 추가 리소스 (있는 경우)
; Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 시작 메뉴 아이콘
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\{#MyAppName} 사용 설명서"; Filename: "{app}\README.txt"; IconIndex: 0; Comment: "SmartCrawler Pro 사용 설명서"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconIndex: 0; Comment: "SmartCrawler Pro 제거"

; 바탕화면 바로가기
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"

; 빠른 실행 바로가기
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"

[Run]
; 설치 완료 후 실행 옵션
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; 설치 완료 후 README 열기 옵션
Filename: "{app}\README.txt"; Description: "사용 설명서 보기"; Flags: postinstall skipifsilent shellexec unchecked

[UninstallDelete]
; 언인스톨 시 삭제할 추가 파일들
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: files; Name: "{app}\config.ini"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp"

[Registry]
; 레지스트리 등록 (프로그램 정보)
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

; 파일 연결 (선택사항)
; Root: HKCR; Subkey: ".crawl"; ValueType: string; ValueName: ""; ValueData: "SmartCrawlerProject"; Flags: uninsdeletevalue
; Root: HKCR; Subkey: "SmartCrawlerProject"; ValueType: string; ValueName: ""; ValueData: "SmartCrawler Project File"; Flags: uninsdeletekey
; Root: HKCR; Subkey: "SmartCrawlerProject\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
; Root: HKCR; Subkey: "SmartCrawlerProject\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Code]
// 사용자 정의 함수들

// 이전 버전 확인
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

// 이전 버전 제거 확인
function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

// 설치 전 이전 버전 제거
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

// 설치 초기화
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;

// 시스템 요구사항 확인
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  
  // Windows 7 이상 요구
  if Version.Major < 6 then begin
    MsgBox('이 프로그램은 Windows 7 이상에서만 실행됩니다.', mbError, MB_OK);
    Result := False;
  end else begin
    Result := True;
  end;
end;

// 설치 완료 메시지
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 추가 설정이나 파일 생성 작업
  end;
end; 