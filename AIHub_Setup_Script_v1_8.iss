[Setup]
AppId={{999ECAE8-60BF-4566-B61D-51F5BFAC7B66}
AppName=AIHub
AppVersion=1.6
AppPublisher=EveriAI, LLC.
AppPublisherURL=https://www.everiai.ai/
AppSupportURL=https://www.everiai.ai/
AppUpdatesURL=https://github.com/everiai-aihub/releases
DefaultDirName={autopf}\AIHub
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultGroupName=AIHub
DisableProgramGroupPage=yes
LicenseFile=C:\src\aihub-client\static\license.txt
OutputBaseFilename=AIHub.Setup.v1.6
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; For auto-updates - we handle service stopping ourselves
CloseApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
FinishedLabelNoIcons=Setup has finished installing [name] on your computer.%n%nAI Hub is now running as a local web service.%n%nOpen your browser to access the application.
FinishedLabel=Setup has finished installing [name] on your computer.%n%nAI Hub is now running and will open in your browser.%n%nYou can also access it anytime at the configured port.

[Dirs]
Name: "{app}\cache"
Name: "{app}\logs"
Name: "{app}\tools"
Name: "{app}\tmp"
Name: "{app}\data"
Name: "{app}\agent_environments"
Name: "{app}\agent_environments\python-bundle"
Name: "{app}\agent_environments\python-bundle-requirements"
Name: "{app}\static\icons"

[Files]
Source: "C:\src\aihub-client\dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\ExecuteQuickJob.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\document_api_server.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\document_job_processor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\job_scheduler_service.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\wsgi_vector_api.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\wsgi_agent_api.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\wsgi_knowledge_api.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\wsgi_executor_service.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\nssm-2.24\win64\nssm.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\.env"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\core_tools.yaml"; DestDir: "{app}"; Flags: ignoreversion 
Source: "C:\src\aihub-client\dist\user_config.py"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\user_prompts.py"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\GeneralAgent.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\assets\prompt_templates\*"; DestDir: "{app}\assets\prompt_templates"; Flags: recursesubdirs createallsubdirs 
; Include bundled Python with installation
Source: "C:\src\aihub-client\dist\python-bundle\*"; DestDir: "{app}\agent_environments\python-bundle"; Flags: ignoreversion recursesubdirs
Source: "C:\src\aihub-client\dist\python-bundle-requirements\*"; DestDir: "{app}\agent_environments\python-bundle-requirements"; Flags: ignoreversion recursesubdirs
Source: "C:\src\aihub-client\dist\static\icons\*"; DestDir: "{app}\static\icons"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\AIHub"; Filename: "{app}\app.exe"
Name: "{group}\Open AI Hub in Browser"; Filename: "http://localhost:5001"; Comment: "Open AI Hub in your web browser"
Name: "{group}\{cm:UninstallProgram,AIHub}"; Filename: "{uninstallexe}"
; Desktop shortcut - opens browser directly
Name: "{commondesktop}\AI Hub"; Filename: "http://localhost:5001"; IconFilename: "{app}\static\icons\aihub.ico"; Comment: "Open AI Hub in your browser"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
; Open browser after fresh install (not during upgrades, not during silent install)
Filename: "cmd.exe"; \
  Parameters: "/c timeout /t 8 /nobreak >nul && start http://localhost:5001"; \
  Description: "Open AI Hub in browser"; \
  Flags: postinstall nowait skipifsilent runhidden shellexec; \
  Check: IsNewInstallation

[Code]
var
  CustomPage: TWizardPage;
  ApiKeyEdit, PortEdit, LocalUserEdit, LocalPwdEdit, LocalDomainEdit, RemoteUserEdit, RemotePwdEdit, RemoteDomainEdit: TEdit;
  ReadOnlyCheckBox: TCheckBox;
  ApiKeyLabel, PortLabel, LocalUserLabel, LocalPwdLabel, LocalDomainLabel, RemoteUserLabel, RemotePwdLabel, RemoteDomainLabel: TLabel;
  ValidateButton: TButton;
  IsUpgrade: Boolean;
  ExistingApiKey: String;
  ExistingInstallPath: String;
  ConfiguredPort: String;

const
  APIValidationURL = 'https://ai-hub-api.azurewebsites.net/validate_license';

function IsNewInstallation(): Boolean;
begin
  Result := not IsUpgrade;
end;

function GetInstalledVersion(): String;
var
  RegValue: String;
begin
  Result := '';
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{999ECAE8-60BF-4566-B61D-51F5BFAC7B66}_is1', 
    'DisplayVersion', RegValue) then
    begin
      Result := RegValue;
      MsgBox('Existing installation detected. AI Hub will be upgraded from ' + Result + ' to ' + '{#SetupSetting("AppVersion")}', mbInformation, MB_OK);
    end;
    
    if Result = '' then
    begin
      if FileExists('c:\Program Files\AIHub\.env') then
        Result := ExpandConstant('{#SetupSetting("AppVersion")}');
    end;
end;

function GetInstallPath(): String;
var
  InstallPath: String;
begin
  Result := '';
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{999ECAE8-60BF-4566-B61D-51F5BFAC7B66}_is1', 
    'InstallLocation', InstallPath) then
    Result := InstallPath;
end;

function ReadEnvFileFromPath(const FilePath: String; const Key: String): String;
var
  Lines: TArrayOfString;
  I: Integer;
  Line: String;
  KeyValue: String;
begin
  Result := '';
  
  if FileExists(FilePath) then
  begin
    if LoadStringsFromFile(FilePath, Lines) then
    begin
      for I := 0 to GetArrayLength(Lines) - 1 do
      begin
        Line := Trim(Lines[I]);
        if (Pos(Key + '=', Line) = 1) then
        begin
          KeyValue := Copy(Line, Length(Key) + 2, Length(Line));
          Result := KeyValue;
          Break;
        end;
      end;
    end;
  end;
end;

function GetConfiguredPort(): String;
var
  EnvPath: String;
  PortValue: String;
begin
  Result := '5001';  // Default port
  
  EnvPath := ExpandConstant('{app}\.env');
  if FileExists(EnvPath) then
  begin
    PortValue := ReadEnvFileFromPath(EnvPath, 'HOST_PORT');
    if PortValue <> '' then
      Result := PortValue;
  end;
  
  Log('Configured port: ' + Result);
  ConfiguredPort := Result;
end;

function EnsureEnvKeyExists(const FilePath, Key, Value: String): Boolean;
var
  Existing: String;
  LineToAdd: String;
begin
  // Returns True if the key already existed or was successfully appended.
  // Returns False only if we attempted to append and failed.
  Result := True;

  Existing := ReadEnvFileFromPath(FilePath, Key);
  if Existing <> '' then
  begin
    Log('Env key already present: ' + Key + '=' + Existing);
    Exit; // nothing to do
  end;

  Log('Env key missing, appending: ' + Key + '=' + Value);
  LineToAdd := #13#10 + Key + '=' + Value + #13#10;
  if not SaveStringToFile(FilePath, LineToAdd, True) then
  begin
    Log('ERROR: Failed to append ' + Key + ' to ' + FilePath);
    Result := False;
  end
  else
    Log('Successfully appended ' + Key + ' to ' + FilePath);
end;

procedure ReadOnlyCheckBoxClick(Sender: TObject);
begin
  LocalUserEdit.ReadOnly := ReadOnlyCheckBox.Checked;
  LocalPwdEdit.ReadOnly := ReadOnlyCheckBox.Checked;
  LocalDomainEdit.ReadOnly := ReadOnlyCheckBox.Checked;

  if ReadOnlyCheckBox.Checked then
  begin
    LocalUserEdit.Color := clBtnFace;
    LocalPwdEdit.Color := clBtnFace;
    LocalDomainEdit.Color := clBtnFace;
  end
  else
  begin
    LocalUserEdit.Color := clWindow;
    LocalPwdEdit.Color := clWindow;
    LocalDomainEdit.Color := clWindow;
  end;
end;

function ValidateApiKey(const ApiKey: string): Boolean;
var
  WinHttpReq: Variant;
  ResponseText: string;
begin
  Result := False;
  try
    WinHttpReq := CreateOleObject('WinHttp.WinHttpRequest.5.1');
    WinHttpReq.Open('GET', APIValidationURL + '/' + ApiKey, False);
    WinHttpReq.Send('');
    ResponseText := WinHttpReq.ResponseText;
    Result := (WinHttpReq.Status = 200) and (Pos('"response":"valid"', ResponseText) > 0);
  except
    MsgBox('Error validating API key.', mbError, MB_OK);
  end;
end;

procedure ValidateButtonClick(Sender: TObject);
begin
  if ValidateApiKey(ApiKeyEdit.Text) then
  begin
    MsgBox('API Key is valid.', mbInformation, MB_OK);
  end
  else
  begin
    MsgBox('Invalid API Key.', mbError, MB_OK);
  end;
end;

procedure ConfigureServiceRecovery(ServiceName: String);
var
  ResultCode: Integer;
begin
  // Configure Windows Service Recovery Options via SC command
  Exec('sc.exe', 'failure "' + ServiceName + '" reset= 86400 actions= restart/60000/restart/300000/restart/600000', 
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  // Set service to restart on non-zero exit codes
  Exec('sc.exe', 'failureflag "' + ServiceName + '" 1', '', 
    SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure StopAndRemoveServices();
var
  ResultCode: Integer;
  Services: array[0..7] of String;
  I: Integer;
begin
  Services[0] := 'AIHub';
  Services[1] := 'AIHubDocAPI';
  Services[2] := 'AIHubDocQueue';
  Services[3] := 'AIHubJobScheduler';
  Services[4] := 'AIHubVectorAPI';
  Services[5] := 'AIHubAgentAPI';
  Services[6] := 'AIHubKnowledgeAPI';
  Services[7] := 'AIHubExecutorService';
  
  Log('Stopping and removing existing services...');
  
  for I := 0 to 7 do
  begin
    // Stop service
    Log('Stopping service: ' + Services[I]);
    Exec('sc.exe', 'stop "' + Services[I] + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(2000); // Give services time to stop gracefully
    
    // Remove service
    Log('Removing service: ' + Services[I]);
    Exec('sc.exe', 'delete "' + Services[I] + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  // Additional wait to ensure all services are fully stopped
  Sleep(3000);
end;

function InitializeSetup(): Boolean;
var
  OldVersion: String;
  EnvFilePath: String;
begin
  Result := True;
  OldVersion := GetInstalledVersion();
  IsUpgrade := (OldVersion <> '');
  
  if IsUpgrade then
  begin
    Log('========================================');
    Log('UPGRADE DETECTED');
    Log('========================================');
    Log('Existing version: ' + OldVersion);
    Log('New version: ' + ExpandConstant('{#SetupSetting("AppVersion")}'));
    
    // Get the existing installation path
    ExistingInstallPath := GetInstallPath();
    
    if ExistingInstallPath = '' then
    begin
      // Try default location
      ExistingInstallPath := ExpandConstant('{autopf}\AIHub');
      Log('Could not read install path from registry, using default: ' + ExistingInstallPath);
    end
    else
    begin
      Log('Found existing installation path: ' + ExistingInstallPath);
    end;
    
    // Build path to .env file
    EnvFilePath := AddBackslash(ExistingInstallPath) + '.env';
    Log('Looking for .env file at: ' + EnvFilePath);
    
    // Try the most common default path
    if not FileExists(EnvFilePath) then
    begin
      Log('File not found, trying the most common path to .env file...');
      EnvFilePath := 'c:\Program Files\AIHub\.env';
    end;
    
    if not FileExists(EnvFilePath) then
    begin
      MsgBox('Could not find .env file at: ' + EnvFilePath + #13#10#13#10 + 
             'The upgrade cannot continue without a valid configuration file.', mbError, MB_OK);
      Log('ERROR: .env file not found');
      Result := False;
      Exit;
    end;
    
    // Read existing API key for validation
    ExistingApiKey := ReadEnvFileFromPath(EnvFilePath, 'API_KEY');
    
    if ExistingApiKey = '' then
    begin
      MsgBox('Could not read API_KEY from .env file at: ' + EnvFilePath + #13#10#13#10 + 
             'Please ensure the .env file contains a valid API_KEY entry.', mbError, MB_OK);
      Log('ERROR: API_KEY not found in .env file');
      Result := False;
      Exit;
    end
    else
    begin
      Log('Successfully read API key from .env file (first 8 chars): ' + Copy(ExistingApiKey, 1, 8) + '...');
    end;
    
    // NOTE: Services will be stopped later in PrepareToInstall(), 
    // AFTER the user has committed to the installation.
    // This prevents breaking the app if the user cancels the wizard.
    
  end
  else
  begin
    Log('========================================');
    Log('FRESH INSTALLATION');
    Log('========================================');
  end;
end;

procedure InitializeWizard;
begin
  CustomPage := CreateCustomPage(wpWelcome, 'Configuration', 'Enter your AIHub configuration details');
  
  // Create and position the labels and controls
  ApiKeyLabel := TLabel.Create(WizardForm);
  ApiKeyLabel.Parent := CustomPage.Surface;
  ApiKeyLabel.Left := 10;
  ApiKeyLabel.Top := 20;
  ApiKeyLabel.Caption := 'License Key:';

  ApiKeyEdit := TEdit.Create(WizardForm);
  ApiKeyEdit.Parent := CustomPage.Surface;
  ApiKeyEdit.Left := 120;
  ApiKeyEdit.Top := ApiKeyLabel.Top - 3;
  ApiKeyEdit.Width := CustomPage.SurfaceWidth - 200;
  ApiKeyEdit.Text := '';

  ValidateButton := TButton.Create(WizardForm);
  ValidateButton.Parent := CustomPage.Surface;
  ValidateButton.Left := ApiKeyEdit.Left + ApiKeyEdit.Width + 10;
  ValidateButton.Top := ApiKeyEdit.Top;
  ValidateButton.Width := 70;
  ValidateButton.Caption := 'Validate';
  ValidateButton.OnClick := @ValidateButtonClick;

  PortLabel := TLabel.Create(WizardForm);
  PortLabel.Parent := CustomPage.Surface;
  PortLabel.Left := 10;
  PortLabel.Top := ApiKeyLabel.Top + 30;
  PortLabel.Caption := 'Port:';

  PortEdit := TEdit.Create(WizardForm);
  PortEdit.Parent := CustomPage.Surface;
  PortEdit.Left := 120;
  PortEdit.Top := PortLabel.Top - 3;
  PortEdit.Width := CustomPage.SurfaceWidth - 130;
  PortEdit.Text := '5001';

  ReadOnlyCheckBox := TCheckBox.Create(WizardForm);
  ReadOnlyCheckBox.Parent := CustomPage.Surface;
  ReadOnlyCheckBox.Left := 10;
  ReadOnlyCheckBox.Top := PortLabel.Top + 30;
  ReadOnlyCheckBox.Width := CustomPage.SurfaceWidth - 20;
  ReadOnlyCheckBox.Caption := 'Use Local System Account';
  ReadOnlyCheckBox.OnClick := @ReadOnlyCheckBoxClick;

  LocalUserLabel := TLabel.Create(WizardForm);
  LocalUserLabel.Parent := CustomPage.Surface;
  LocalUserLabel.Left := 10;
  LocalUserLabel.Top := ReadOnlyCheckBox.Top + 30;
  LocalUserLabel.Caption := 'Local User:';

  LocalUserEdit := TEdit.Create(WizardForm);
  LocalUserEdit.Parent := CustomPage.Surface;
  LocalUserEdit.Left := 120;
  LocalUserEdit.Top := LocalUserLabel.Top - 3;
  LocalUserEdit.Width := CustomPage.SurfaceWidth - 130;
  LocalUserEdit.Text := '';

  LocalPwdLabel := TLabel.Create(WizardForm);
  LocalPwdLabel.Parent := CustomPage.Surface;
  LocalPwdLabel.Left := 10;
  LocalPwdLabel.Top := LocalUserLabel.Top + 30;
  LocalPwdLabel.Caption := 'Local Password:';

  LocalPwdEdit := TEdit.Create(WizardForm);
  LocalPwdEdit.Parent := CustomPage.Surface;
  LocalPwdEdit.Left := 120;
  LocalPwdEdit.Top := LocalPwdLabel.Top - 3;
  LocalPwdEdit.Width := CustomPage.SurfaceWidth - 130;
  LocalPwdEdit.PasswordChar := '*';
  LocalPwdEdit.Text := '';

  LocalDomainLabel := TLabel.Create(WizardForm);
  LocalDomainLabel.Parent := CustomPage.Surface;
  LocalDomainLabel.Left := 10;
  LocalDomainLabel.Top := LocalPwdLabel.Top + 30;
  LocalDomainLabel.Caption := 'Local Domain:';

  LocalDomainEdit := TEdit.Create(WizardForm);
  LocalDomainEdit.Parent := CustomPage.Surface;
  LocalDomainEdit.Left := 120;
  LocalDomainEdit.Top := LocalDomainLabel.Top - 3;
  LocalDomainEdit.Width := CustomPage.SurfaceWidth - 130;
  LocalDomainEdit.Text := '';

  RemoteUserLabel := TLabel.Create(WizardForm);
  RemoteUserLabel.Parent := CustomPage.Surface;
  RemoteUserLabel.Left := 10;
  RemoteUserLabel.Top := LocalDomainLabel.Top + 30;
  RemoteUserLabel.Caption := 'Remote User:';

  RemoteUserEdit := TEdit.Create(WizardForm);
  RemoteUserEdit.Parent := CustomPage.Surface;
  RemoteUserEdit.Left := 120;
  RemoteUserEdit.Top := RemoteUserLabel.Top - 3;
  RemoteUserEdit.Width := CustomPage.SurfaceWidth - 130;
  RemoteUserEdit.Text := '';

  RemotePwdLabel := TLabel.Create(WizardForm);
  RemotePwdLabel.Parent := CustomPage.Surface;
  RemotePwdLabel.Left := 10;
  RemotePwdLabel.Top := RemoteUserLabel.Top + 30;
  RemotePwdLabel.Caption := 'Remote Password:';

  RemotePwdEdit := TEdit.Create(WizardForm);
  RemotePwdEdit.Parent := CustomPage.Surface;
  RemotePwdEdit.Left := 120;
  RemotePwdEdit.Top := RemotePwdLabel.Top - 3;
  RemotePwdEdit.Width := CustomPage.SurfaceWidth - 130;
  RemotePwdEdit.PasswordChar := '*';
  RemotePwdEdit.Text := '';

  RemoteDomainLabel := TLabel.Create(WizardForm);
  RemoteDomainLabel.Parent := CustomPage.Surface;
  RemoteDomainLabel.Left := 10;
  RemoteDomainLabel.Top := RemotePwdLabel.Top + 30;
  RemoteDomainLabel.Caption := 'Remote Domain:';

  RemoteDomainEdit := TEdit.Create(WizardForm);
  RemoteDomainEdit.Parent := CustomPage.Surface;
  RemoteDomainEdit.Left := 120;
  RemoteDomainEdit.Top := RemoteDomainLabel.Top - 3;
  RemoteDomainEdit.Width := CustomPage.SurfaceWidth - 130;
  RemoteDomainEdit.Text := '';

  // Initialize the fields as readonly if the checkbox is checked
  ReadOnlyCheckBoxClick(ReadOnlyCheckBox);
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // Skip configuration page during upgrades
  Result := IsUpgrade and (PageID = CustomPage.ID);
  
  if Result then
    Log('Skipping configuration page - this is an upgrade');
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  // This function is called AFTER the user clicks Install,
  // but BEFORE files are copied. This is the safe time to stop services.
  Result := '';  // Empty string means continue with installation
  NeedsRestart := False;
  
  if IsUpgrade then
  begin
    Log('========================================');
    Log('STOPPING SERVICES BEFORE FILE UPDATE');
    Log('========================================');
    
    // Now it's safe to stop services - user has committed to the upgrade
    StopAndRemoveServices();
    
    Log('Services stopped successfully - proceeding with file update');
  end;
end;

procedure InstallServices();
var
  ResultCode: Integer;
  EnvConfigFile: String;
  LocalUser, LocalPwd, LocalDomain: String;
  UseSystemAccount: Boolean;
begin
  EnvConfigFile := ExpandConstant('{app}\.env');
  
  // Read service account settings from .env file if it's an upgrade
  if IsUpgrade then
  begin
    Log('Reading service configuration from existing .env file');
    LocalUser := ReadEnvFileFromPath(EnvConfigFile, 'WINTASK_USER');
    LocalPwd := ReadEnvFileFromPath(EnvConfigFile, 'WINTASK_PWD');
    LocalDomain := ReadEnvFileFromPath(EnvConfigFile, 'LOCAL_DOMAIN');
    UseSystemAccount := (LocalUser = '') or (LocalDomain = '');
    Log('Service will run as: ' + LocalDomain + '\' + LocalUser);
  end
  else
  begin
    Log('Using new installation service configuration');
    LocalUser := LocalUserEdit.Text;
    LocalPwd := LocalPwdEdit.Text;
    LocalDomain := LocalDomainEdit.Text;
    UseSystemAccount := ReadOnlyCheckBox.Checked;
  end;
  
  WizardForm.StatusLabel.Caption := 'Installing services...';
  Log('Installing AIHub services...');
  
  // Register the core application as a Windows service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHub "' + ExpandConstant('{app}\app.exe') + '" ' +
    '"--env-file=' + EnvConfigFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHub ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Log('AIHub: Set service account to ' + LocalDomain + '\' + LocalUser);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHub Description "AI Hub core service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHub');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHub', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHub service started');
  
  // Register the document API service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubDocAPI "' + ExpandConstant('{app}\document_api_server.exe') + '" ' +
    '"--env-file=' + EnvConfigFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocAPI ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocAPI Description "AI Hub document API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubDocAPI');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubDocAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubDocAPI service started');
  
  // Register the document queue service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubDocQueue "' + ExpandConstant('{app}\document_job_processor.exe') + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocQueue ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocQueue Description "AI Hub document job queue service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubDocQueue');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubDocQueue', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubDocQueue service started');
    
  // Register the job scheduler service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubJobScheduler "' + ExpandConstant('{app}\job_scheduler_service.exe') + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubJobScheduler ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubJobScheduler Description "AI Hub job scheduler service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubJobScheduler');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubJobScheduler', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubJobScheduler service started');

  // Register the vector API service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubVectorAPI "' + ExpandConstant('{app}\wsgi_vector_api.exe') + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubVectorAPI ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubVectorAPI Description "AI Hub vector API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubVectorAPI');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubVectorAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubVectorAPI service started');
  
  // Register the agent API service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubAgentAPI "' + ExpandConstant('{app}\wsgi_agent_api.exe') + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubAgentAPI ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubAgentAPI Description "AI Hub agent API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubAgentAPI');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubAgentAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubAgentAPI service started');
  
  // Register the knowledge API service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubKnowledgeAPI "' + ExpandConstant('{app}\wsgi_knowledge_api.exe') + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubKnowledgeAPI ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubKnowledgeAPI Description "AI Hub knowledge API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubKnowledgeAPI');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubKnowledgeAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubKnowledgeAPI service started');
  
  // Register the executor service
  ShellExec('', ExpandConstant('{app}\nssm.exe'),
    'install AIHubExecutorService "' + ExpandConstant('{app}\wsgi_executor_service.exe') + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if not UseSystemAccount then
  begin
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubExecutorService ObjectName ' + LocalDomain + '\' + LocalUser + ' ' + LocalPwd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubExecutorService Description "AI Hub executor service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  ConfigureServiceRecovery('AIHubExecutorService');
  Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubExecutorService', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('AIHubExecutorService service started');
  
  Log('All services installed and started successfully');
  
  // Get the configured port for browser launch
  GetConfiguredPort();
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: TFileStream;
  ConfigText: String;
  EnvConfigFile: String;
  AppRootVal: String;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    EnvConfigFile := ExpandConstant('{app}\.env');
    
    if IsUpgrade then
    begin
      // For upgrades, validate the existing API key
      WizardForm.StatusLabel.Caption := 'Validating existing license...';
      Log('Validating existing API key');
      
      if not ValidateApiKey(ExistingApiKey) then
      begin
        MsgBox('The API Key in your existing configuration is no longer valid.' + #13#10#13#10 + 
               'Installation will now abort. Please contact support.', mbError, MB_OK);
        Log('ERROR: Existing API key validation failed');
        Abort;
      end;
      
      Log('Existing API key validated successfully');
      
      // --- NEW: ensure APP_ROOT exists during upgrade ---
      AppRootVal := ReadEnvFileFromPath(EnvConfigFile, 'APP_ROOT');
      if AppRootVal = '' then
      begin
        Log('APP_ROOT not found in .env during upgrade; adding it now...');
        if not EnsureEnvKeyExists(EnvConfigFile, 'APP_ROOT', ExpandConstant('{app}')) then
        begin
          // Don't abort the whole install; just warn. Services can still run,
          // but APP_ROOT is helpful for your app. Adjust severity if desired.
          MsgBox('Warning: Failed to write APP_ROOT to .env.' + #13#10 +
                 'You may need to add it manually: APP_ROOT=' + ExpandConstant('{app}'),
                 mbError, MB_OK);
        end;
      end
      else
        Log('APP_ROOT already present: ' + AppRootVal);
      // --- END NEW ---
      
      // --- VERIFY: WORKFLOW_TRAINING_CAPTURE_ENABLED ---
      if not EnsureEnvKeyExists(EnvConfigFile, 'WORKFLOW_TRAINING_CAPTURE_ENABLED', 'false') then
      begin
        // Don't abort the whole install; just warn. Services can still run,
        MsgBox('Warning: Failed to write WORKFLOW_TRAINING_CAPTURE_ENABLED to .env.' + #13#10 +
               'You may need to add it manually',
               mbError, MB_OK);
      end;

      // --- VERIFY: WORKFLOW_TRAINING_CAPTURE_PATH ---
      if not EnsureEnvKeyExists(EnvConfigFile, 'WORKFLOW_TRAINING_CAPTURE_PATH', './training_data/workflows') then
      begin
        // Don't abort the whole install; just warn. Services can still run,
        MsgBox('Warning: Failed to write WORKFLOW_TRAINING_CAPTURE_PATH to .env.' + #13#10 +
               'You may need to add it manually',
               mbError, MB_OK);
      end;

      // --- VERIFY: USE_TWO_STAGE_ARCHITECTURE ---
      if not EnsureEnvKeyExists(EnvConfigFile, 'USE_TWO_STAGE_ARCHITECTURE', 'true') then
      begin
        // Don't abort the whole install; just warn. Services can still run,
        MsgBox('Warning: Failed to write USE_TWO_STAGE_ARCHITECTURE to .env.' + #13#10 +
               'You may need to add it manually',
               mbError, MB_OK);
      end;
      
      // --- VERIFY: USE_WORKFLOW_EXECUTOR_SERVICE ---
      if not EnsureEnvKeyExists(EnvConfigFile, 'USE_WORKFLOW_EXECUTOR_SERVICE', 'true') then
      begin
        // Don't abort the whole install; just warn. Services can still run,
        MsgBox('Warning: Failed to write USE_WORKFLOW_EXECUTOR_SERVICE to .env.' + #13#10 +
               'You may need to add it manually',
               mbError, MB_OK);
      end;
      
      // --- VERIFY: KNOWLEDGE_SERVER_THREADS ---
      if not EnsureEnvKeyExists(EnvConfigFile, 'KNOWLEDGE_SERVER_THREADS', '2') then
      begin
        // Don't abort the whole install; just warn. Services can still run,
        MsgBox('Warning: Failed to write KNOWLEDGE_SERVER_THREADS to .env.' + #13#10 +
               'You may need to add it manually',
               mbError, MB_OK);
      end;
      
      // --- VERIFY: EXECUTOR_SERVICE_THREADS ---
      if not EnsureEnvKeyExists(EnvConfigFile, 'EXECUTOR_SERVICE_THREADS', '4') then
      begin
        // Don't abort the whole install; just warn. Services can still run,
        MsgBox('Warning: Failed to write EXECUTOR_SERVICE_THREADS to .env.' + #13#10 +
               'You may need to add it manually',
               mbError, MB_OK);
      end;
      
    end
    else
    begin
      // For new installations, validate the entered API key
      WizardForm.StatusLabel.Caption := 'Validating API key...';
      Log('Validating new API key');
      
      if not ValidateApiKey(ApiKeyEdit.Text) then
      begin
        MsgBox('Invalid API Key. Installation will now abort.', mbError, MB_OK);
        Log('ERROR: New API key validation failed');
        Abort;
      end;

      // Create the configuration file for new installations
      WizardForm.StatusLabel.Caption := 'Writing configuration...';
      Log('Creating new .env configuration file');
      
      try
        ConfigText := #13#10 +
          'API_KEY=' + ApiKeyEdit.Text + #13#10 +
          'HOST_PORT=' + PortEdit.Text + #13#10 +
          'WINTASK_USER=' + LocalUserEdit.Text + #13#10 +
          'WINTASK_PWD=' + LocalPwdEdit.Text + #13#10 +
          'LOCAL_DOMAIN=' + LocalDomainEdit.Text + #13#10 +
          'WINRM_USER=' + RemoteUserEdit.Text + #13#10 +
          'WINRM_PWD=' + RemotePwdEdit.Text + #13#10 +
          'WINRM_DOMAIN=' + RemoteDomainEdit.Text + #13#10 +
          'APP_ROOT=' + ExpandConstant('{app}') + #13#10;
        SaveStringToFile(EnvConfigFile, ConfigText, True);
        Log('Configuration file created successfully');
      finally
        ConfigFile := nil;
      end;
    end;

    // Install services (works for both new installs and upgrades)
    InstallServices();
    
    // For upgrades, show completion message and open browser
    if IsUpgrade then
    begin
      Log('Upgrade complete - opening browser');
      // Small delay to ensure services are fully started
      Sleep(60000);
      // Open browser to the application
      ShellExec('open', 'http://localhost:' + ConfiguredPort, '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
    end;
  end;
end;

[Run]

[UninstallRun]
Filename: "{app}\nssm.exe"; Parameters: "stop AIHub"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHub confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubDocAPI"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubDocAPI confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubDocQueue"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubDocQueue confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubJobScheduler"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubJobScheduler confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubVectorAPI"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubVectorAPI confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubAgentAPI"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubAgentAPI confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubKnowledgeAPI"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubKnowledgeAPI confirm"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "stop AIHubExecutorService"; Flags: runhidden waituntilterminated
Filename: "{app}\nssm.exe"; Parameters: "remove AIHubExecutorService confirm"; Flags: runhidden

[UninstallDelete]
Type: files; Name: "{app}\*.exe"
Type: files; Name: "{app}\*.yaml"
Type: files; Name: "{app}\cache\*.*"
Type: files; Name: "{app}\logs\*.*"
//Type: files; Name: "{app}\tools\*.*"       // Keep client tools
Type: files; Name: "{app}\flask_session\*.*"
Type: files; Name: "{app}\assets\prompt_templates\*.*"
Type: files; Name: "{app}\assets\*.*"
Type: files; Name: "{app}\exports\charts\*.*"
Type: files; Name: "{app}\exports\*.*"
Type: files; Name: "{app}\tmp\*.*"
Type: files; Name: "{app}\temp\*.*"
Type: files; Name: "{app}\uploads\*.*"
Type: files; Name: "{app}\schemas\*.*"
Type: files; Name: "{app}\*.dat"
Type: files; Name: "{app}\static\*.*"
Type: files; Name: "{app}\agent_environments\python-bundle\*.*"
Type: files; Name: "{app}\agent_environments\python-bundle-requirements\*.*"
Type: dirifempty; Name: "{app}\cache"
Type: dirifempty; Name: "{app}\logs"
Type: dirifempty; Name: "{app}\tools"
Type: dirifempty; Name: "{app}\flask_session"
Type: dirifempty; Name: "{app}\assets\prompt_templates"
Type: dirifempty; Name: "{app}\assets"
Type: dirifempty; Name: "{app}\exports\charts"
Type: dirifempty; Name: "{app}\exports"
Type: dirifempty; Name: "{app}\tmp"
Type: dirifempty; Name: "{app}\temp"
Type: dirifempty; Name: "{app}\uploads"
Type: dirifempty; Name: "{app}\schemas"
Type: dirifempty; Name: "{app}\static"
Type: dirifempty; Name: "{app}\agent_environments\python-bundle"
Type: dirifempty; Name: "{app}\agent_environments\python-bundle-requirements"
Type: dirifempty; Name: "{app}"
