# WordPress 测试环境便捷脚本（Windows / PowerShell）
# 用法示例：
#   .\run.ps1 init      # 生成 .env
#   .\run.ps1 up        # 启动被测环境
#   .\run.ps1 seed      # 初始化站点与测试数据
#   .\run.ps1 status    # 查看容器与站点状态
#   .\run.ps1 reset     # 销毁并重建（数据全删）
param(
    [Parameter(Position = 0)]
    [ValidateSet('init', 'up', 'seed', 'down', 'reset', 'status', 'logs', 'old-up', 'old-seed', 'old-down', 'wp')]
    [string]$Cmd = 'status',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Ensure-Env {
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
        Write-Host '已从 .env.example 生成 .env，请按需修改端口与数据量。' -ForegroundColor Yellow
    }
}

switch ($Cmd) {
    'init' {
        Ensure-Env
        Write-Host '环境变量文件就绪。下一步：.\run.ps1 up' -ForegroundColor Green
    }

    'up' {
        Ensure-Env
        docker compose up -d
        Write-Host ''
        Write-Host '等待 WordPress 就绪（首次约 30–60 秒）...' -ForegroundColor Cyan
        Start-Sleep -Seconds 15
        docker compose ps
        Write-Host ''
        Write-Host '访问：http://localhost:8080  后台：http://localhost:8080/wp-admin/' -ForegroundColor Green
    }

    'seed' {
        Ensure-Env
        docker compose --profile tools run --rm --entrypoint sh wpcli /init/seed.sh
    }

    'status' {
        docker compose ps
        Write-Host ''
        try {
            $r = Invoke-WebRequest -Uri 'http://localhost:8080/wp-login.php' -UseBasicParsing -TimeoutSec 5
            Write-Host ("站点响应：HTTP {0}" -f $r.StatusCode) -ForegroundColor Green
        } catch {
            Write-Host '站点暂无响应，可能容器未启动。' -ForegroundColor Yellow
        }
    }

    'down' {
        docker compose down
    }

    'reset' {
        $ans = Read-Host '将删除容器与全部数据卷，输入 YES 确认'
        if ($ans -eq 'YES') {
            docker compose down -v
            Write-Host '已重置，重新执行 .\run.ps1 up 与 .\run.ps1 seed' -ForegroundColor Green
        } else {
            Write-Host '已取消'
        }
    }

    'logs' {
        docker compose logs -f --tail 100
    }

    'old-up' {
        Ensure-Env
        docker compose -p wp-old -f docker-compose.old.yml up -d
        Write-Host '旧版本对照环境：http://localhost:8081' -ForegroundColor Green
    }

    'old-seed' {
        docker compose -p wp-old -f docker-compose.old.yml --profile tools run --rm --entrypoint sh wpcli /init/seed.sh
    }

    'old-down' {
        docker compose -p wp-old -f docker-compose.old.yml down
    }

    'wp' {
        if (-not $Rest -or $Rest.Count -eq 0) {
            Write-Host '用法：.\run.ps1 wp "post list --format=count"' -ForegroundColor Yellow
            return
        }
        docker compose --profile tools run --rm wpcli $Rest
    }
}
