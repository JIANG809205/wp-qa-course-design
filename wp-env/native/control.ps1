# 服务控制脚本（Windows 侧调用 WSL）
# 用法：.\control.ps1 start | stop | restart | status
param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'stop', 'restart', 'status')]
    [string]$Cmd = 'status'
)

$ErrorActionPreference = 'Stop'
$env:WSL_UTF8 = '1'
$script = '/mnt/e/软件质量保证与测试课程设计/wp-env/native/svc.sh'

& wsl -d Ubuntu-22.04 -u root -- bash $script $Cmd
