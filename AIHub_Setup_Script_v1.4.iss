[Setup]
AppId={{999ECAE8-60BF-4566-B61D-51F5BFAC7B66}
AppName=AIHub
AppVersion=1.4.r7
AppPublisher=EveriAI, LLC.
AppPublisherURL=https://www.ai-hub-api.azurewebsites.net/
AppSupportURL=https://www.ai-hub-api.azurewebsites.net/
AppUpdatesURL=https://www.ai-hub-api.azurewebsites.net/
DefaultDirName={autopf}\AIHub
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultGroupName=AIHub
DisableProgramGroupPage=yes
LicenseFile=C:\src\aihub-client\static\license.txt
OutputBaseFilename=AIHub Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\cache"
Name: "{app}\logs"
Name: "{app}\tools"
Name: "{app}\tmp"
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
Source: "C:\src\nssm-2.24\win64\nssm.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\dist\.env"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\core_tools.yaml"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\user_config.py"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\user_prompts.py"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "C:\src\aihub-client\dist\GeneralAgent.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\src\aihub-client\assets\prompt_templates\*"; DestDir: "{app}\assets\prompt_templates"; Flags: recursesubdirs createallsubdirs onlyifdoesntexist
; Include bundled Python with installation
Source: "C:\src\aihub-client\dist\python-bundle\*"; DestDir: "{app}\agent_environments\python-bundle"; Flags: ignoreversion recursesubdirs
Source: "C:\src\aihub-client\dist\python-bundle-requirements\*"; DestDir: "{app}\agent_environments\python-bundle-requirements"; Flags: ignoreversion recursesubdirs
Source: "C:\src\aihub-client\dist\static\icons\*"; DestDir: "{app}\static\icons"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\AIHub"; Filename: "{app}\app.exe"
Name: "{group}\{cm:UninstallProgram,AIHub}"; Filename: "{uninstallexe}"

[Code]
var
  CustomPage: TWizardPage;
  ApiKeyEdit, PortEdit, LocalUserEdit, LocalPwdEdit, LocalDomainEdit, RemoteUserEdit, RemotePwdEdit, RemoteDomainEdit: TEdit;
  ReadOnlyCheckBox: TCheckBox;
  ApiKeyLabel, PortLabel, LocalUserLabel, LocalPwdLabel, LocalDomainLabel, RemoteUserLabel, RemotePwdLabel, RemoteDomainLabel: TLabel;
  ValidateButton: TButton;

const
  APIValidationURL = 'https://ai-hub-api.azurewebsites.net/validate_license';

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
  // First failure: Restart after 60 seconds (60000 milliseconds)
  // Second failure: Restart after 5 minutes (300000 milliseconds)
  // Subsequent failures: Restart after 10 minutes (600000 milliseconds)
  // Reset failure count after 1 day (86400 seconds)
  Exec('sc.exe', 'failure "' + ServiceName + '" reset= 86400 actions= restart/60000/restart/300000/restart/600000', 
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  //Log('Configured service recovery options for ' + ServiceName);

  // Set service to restart on non-zero exit codes
  Exec('sc.exe', 'failureflag "' + ServiceName + '" 1', '', 
    SW_HIDE, ewWaitUntilTerminated, ResultCode);
  //Log('Configured service to restart on non-zero exit codes for ' + ServiceName);
end;

procedure InitializeWizard;
begin
  CustomPage := CreateCustomPage(wpWelcome, 'Configuration', 'Configuration');
  
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

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: TFileStream;
  ConfigText: String;
  EnvConfigFile: String;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Validate the API key
    WizardForm.StatusLabel.Caption := 'Validating API key...';
    if not ValidateApiKey(ApiKeyEdit.Text) then
    begin
      MsgBox('Invalid API Key. Installation will now abort.', mbError, MB_OK);
      Abort;
    end;

    // Create and write to the configuration file
    WizardForm.StatusLabel.Caption := 'Writing config...';
    EnvConfigFile := ExpandConstant('{app}\.env');
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
    finally
      ConfigFile := nil;
    end;

    WizardForm.StatusLabel.Caption := 'Installing services...';
    // Register the core application as a Windows service with the provided parameters
    ShellExec('', ExpandConstant('{app}\nssm.exe'),
      'install AIHub "' + ExpandConstant('{app}\app.exe') + '" ' +
      '"--env-file=' + ExpandConstant('{app}\.env') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Set the service account details if the checkbox is not checked
    if not ReadOnlyCheckBox.Checked then
    begin
      Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHub ObjectName ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text + ' ' + LocalPwdEdit.Text, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Setting service account: Service ObjectName set to: ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text);
    end;
    
    // Set the service description
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHub Description "AI Hub core service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Configure recovery options
    ConfigureServiceRecovery('AIHub');

    // Start the service
    Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHub', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    
    // Register the document service API as a Windows service with the provided parameters
    ShellExec('', ExpandConstant('{app}\nssm.exe'),
      'install AIHubDocAPI "' + ExpandConstant('{app}\document_api_server.exe') + '" ' +
      '"--env-file=' + ExpandConstant('{app}\.env') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Set the service account details if the checkbox is not checked
    if not ReadOnlyCheckBox.Checked then
    begin
      Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocAPI ObjectName ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text + ' ' + LocalPwdEdit.Text, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Setting AIHubDocAPI service account: Service ObjectName set to: ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text);
    end;
    
    // Set the service description
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocAPI Description "AI Hub document API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Configure recovery options
    ConfigureServiceRecovery('AIHubDocAPI');

    // Start the service
    Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubDocAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Register the document queue service as a Windows service (with no arguments)
    ShellExec('', ExpandConstant('{app}\nssm.exe'),
      'install AIHubDocQueue "' + ExpandConstant('{app}\document_job_processor.exe') + '"',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Set the service account details if the checkbox is not checked
    if not ReadOnlyCheckBox.Checked then
    begin
      Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocQueue ObjectName ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text + ' ' + LocalPwdEdit.Text, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Setting AIHubDocQueue service account: Service ObjectName set to: ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text);
    end;
    
    // Set the service description
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubDocQueue Description "AI Hub document job queue service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Configure recovery options
    ConfigureServiceRecovery('AIHubDocQueue');

    // Start the service
    Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubDocQueue', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      
    // Register the job scheduler service as a Windows service (with no arguments)
    ShellExec('', ExpandConstant('{app}\nssm.exe'),
      'install AIHubJobScheduler "' + ExpandConstant('{app}\job_scheduler_service.exe') + '"',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Set the service account details if the checkbox is not checked
    if not ReadOnlyCheckBox.Checked then
    begin
      Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubJobScheduler ObjectName ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text + ' ' + LocalPwdEdit.Text, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Setting AIHubJobScheduler service account: Service ObjectName set to: ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text);
    end;
    
    // Set the service description
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubJobScheduler Description "AI Hub job scheduler service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Configure recovery options
    ConfigureServiceRecovery('AIHubJobScheduler');

    // Start the service
    Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubJobScheduler', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Register the vector api service as a Windows service (with no arguments)
    ShellExec('', ExpandConstant('{app}\nssm.exe'),
      'install AIHubVectorAPI "' + ExpandConstant('{app}\wsgi_vector_api.exe') + '"',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Set the service account details if the checkbox is not checked
    if not ReadOnlyCheckBox.Checked then
    begin
      Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubVectorAPI ObjectName ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text + ' ' + LocalPwdEdit.Text, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Setting AIHubVectorAPI service account: Service ObjectName set to: ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text);
    end;
    
    // Set the service description
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubVectorAPI Description "AI Hub vector API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Configure recovery options
    ConfigureServiceRecovery('AIHubVectorAPI');

    // Start the service
    Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubVectorAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Register the vector api service as a Windows service (with no arguments)
    ShellExec('', ExpandConstant('{app}\nssm.exe'),
      'install AIHubAgentAPI "' + ExpandConstant('{app}\wsgi_agent_api.exe') + '"',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Set the service account details if the checkbox is not checked
    if not ReadOnlyCheckBox.Checked then
    begin
      Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubAgentAPI ObjectName ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text + ' ' + LocalPwdEdit.Text, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Setting AIHubAgentAPI service account: Service ObjectName set to: ' + LocalDomainEdit.Text + '\' + LocalUserEdit.Text);
    end;
    
    // Set the service description
    Exec(ExpandConstant('{app}\nssm.exe'), 'set AIHubAgentAPI Description "AI Hub agent API service"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Configure recovery options
    ConfigureServiceRecovery('AIHubAgentAPI');

    // Start the service
    Exec(ExpandConstant('{app}\nssm.exe'), 'start AIHubAgentAPI', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
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
