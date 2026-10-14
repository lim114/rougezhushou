$ErrorActionPreference='Stop'
$taskRoot=(Get-Location).Path
$taskAllBefore=@('local-settings.json','.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/config.json')
$taskFingerprints=[ordered]@{}
foreach ($taskFile in $taskAllBefore) {if (Test-Path -LiteralPath $taskFile) {$taskFingerprints[$taskFile]=(Get-FileHash -LiteralPath $taskFile -Algorithm SHA256).Hash}}
$taskFingerprints | ConvertTo-Json | Set-Content -LiteralPath .cache/section278-private-before.json -Encoding utf8
$taskBefore=Get-Content -LiteralPath .cache/section278-private-before.json -Raw | ConvertFrom-Json -AsHashtable
$taskOld=Get-Process -Id 12740 -ErrorAction Stop
$taskCim=Get-CimInstance Win32_Process -Filter 'ProcessId = 12740'
if ($taskOld.MainWindowTitle -ne '黑流树海助手 0.91 · 局外计算与节点测试（234）' -or $taskOld.StartTime -ne [datetime]'2026-10-15T00:54:22.7962559+08:00' -or $taskCim.CommandLine -notmatch ' -m rouge\.app$') { throw 'Owned original window changed; do not close' }
$taskChangedBefore=0
foreach ($taskFile in $taskBefore.Keys) {
  if (-not (Test-Path -LiteralPath $taskFile) -or (Get-FileHash -LiteralPath $taskFile -Algorithm SHA256).Hash -ne $taskBefore[$taskFile]) { $taskChangedBefore++ }
}
if ($taskChangedBefore -ne 0) { throw 'Private baseline changed before restart; preserve current user state' }
if (-not $taskOld.CloseMainWindow()) { throw 'Original refused normal close' }
if (-not $taskOld.WaitForExit(10000)) { throw 'Original did not exit normally' }
$taskLaunch=Start-Process -FilePath (Join-Path $taskRoot '.venv\Scripts\pythonw.exe') -ArgumentList @('-m','rouge.app') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru
$taskWindows=@()
for ($taskTry=0;$taskTry -lt 20;$taskTry++) {
  Start-Sleep -Milliseconds 500
  $taskWindows=@(Get-Process -Name pythonw -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -eq '黑流树海助手 0.91 · 局外计算与节点测试（234）' -and $_.StartTime -ge $taskLaunch.StartTime.AddSeconds(-1)})
  if ($taskWindows.Count -eq 1 -and $taskWindows[0].MainWindowHandle -ne 0 -and $taskWindows[0].Responding) { break }
}
if ($taskWindows.Count -ne 1 -or $taskWindows[0].MainWindowHandle -eq 0 -or -not $taskWindows[0].Responding) { throw 'No responding original project window found' }
$taskChanged=0
foreach ($taskFile in $taskBefore.Keys) {
  if (-not (Test-Path -LiteralPath $taskFile) -or (Get-FileHash -LiteralPath $taskFile -Algorithm SHA256).Hash -ne $taskBefore[$taskFile]) { $taskChanged++ }
}
$taskAll=@('local-settings.json','.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/config.json')
$taskNew=@($taskAll | Where-Object {(Test-Path -LiteralPath $_) -and -not $taskBefore.ContainsKey($_)}).Count
$taskReport=[ordered]@{section=278;phase='current_source_skill_data_cost_reference';parent_pid=$taskLaunch.Id;main_pid=@($taskWindows.Id);main_started_at=$taskWindows[0].StartTime.ToString('o');visible_window_handles=@($taskWindows.MainWindowHandle.ToInt64());responding=@($taskWindows.Responding);caption=@($taskWindows.MainWindowTitle);caption_is_legacy_not_authoritative_section_count=$true;prior_owned_main_pid=12740;prior_owned_main_exit_confirmed_before_launch=$true;native_original_window_startup=$true;game_operated=$false;chat_sent=$false;scope='Original current app normal restart after skill cost transformations and independent update qualification. No game/chat or historical private integration.';private_json_files_checked=$taskBefore.Count;private_json_files_changed=$taskChanged;private_json_new_files=$taskNew;desktop_visually_inspected_with='pending'}
$taskReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath verification/sections/277-main-window.json -Encoding utf8
if ($taskChanged -ne 0 -or $taskNew -ne 0) { throw 'Private fingerprints changed; do not restore old state' }
[pscustomobject]@{responding=$taskWindows[0].Responding;main_pid=$taskWindows[0].Id;private_files_changed=$taskChanged;private_new_files=$taskNew}
