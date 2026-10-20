@echo off
rem Space Blaster - booth launcher (Windows). Runs serve.ps1 without needing a
rem changed PowerShell execution policy; double-click it or run: serve.cmd [PORT]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1" %*
