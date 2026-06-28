# ============================================================
#  Script: setup_task_scheduler.ps1
#  Mo ta : Dang ky Task Scheduler tu dong chay backup luc 2h sang
#  Chay bang: PowerShell (Run as Administrator)
# ============================================================

$TaskName    = "CinemaDB_DailyBackup"
$ScriptPath  = "D:\HQTCSDL\Cinema_management\backup\backup_cinemadb.bat"
$TriggerTime = "02:00"

# Kiem tra file bat ton tai
if (-Not (Test-Path $ScriptPath)) {
    Write-Error "Khong tim thay file: $ScriptPath"
    exit 1
}

# Xoa task cu neu ton tai
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Tao Action: chay file .bat
$Action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`""

# Tao Trigger: moi ngay luc 2h sang
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Cai dat: chay du khi may bat sau gio dang ky
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -WakeToRun:$false

# Dang ky vao Task Scheduler (chay voi quyen SYSTEM)
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Force

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host " Da dang ky Task Scheduler thanh cong!" -ForegroundColor Green
Write-Host " Ten Task : $TaskName" -ForegroundColor Cyan
Write-Host " Chay vao : Moi ngay luc $TriggerTime" -ForegroundColor Cyan
Write-Host " Script   : $ScriptPath" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Kiem tra trong Task Scheduler: taskschd.msc" -ForegroundColor Yellow
