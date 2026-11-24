# Docker 测试栈控制（Windows 侧）
# 用法：.\control.ps1 start | stop | restart | status | reset
param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'reset')]
    [string]$Cmd = 'status'
)

$ErrorActionPreference = 'Stop'
$env:WSL_UTF8 = '1'
$script = '/mnt/e/软件质量保证与测试课程设计/wp-env/local/stack.sh'

& wsl -d Ubuntu-22.04 -u root -- bash $script $Cmd
