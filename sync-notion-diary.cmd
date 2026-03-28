@echo off
cd /d "%~dp0"
type sync-notion-diary-prompt.txt | claude -p --dangerously-skip-permissions
