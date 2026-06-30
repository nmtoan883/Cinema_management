@echo off
:: ============================================================
::  Script: backup_cinemadb.bat
::  Mo ta : Tu dong sao luu CSDL CinemaDB vao luc 2h sang
::  Su dung: Dang ky vao Windows Task Scheduler
:: ============================================================

:: ---------- CAU HINH - chinh sua theo may cua ban ----------
SET MYSQL_USER=root
SET MYSQL_PASS=your_password_here
SET MYSQL_HOST=localhost
SET MYSQL_PORT=3306
SET DB_NAME=CinemaDB

:: Thu muc luu file backup (se tu tao neu chua co)
SET BACKUP_DIR=D:\HQTCSDL\Cinema_management\backup\dumps

:: Duong dan den mysqldump.exe (chinh lai neu cai MySQL o cho khac)
SET MYSQLDUMP="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
:: -----------------------------------------------------------

:: Tao thu muc neu chua ton tai
IF NOT EXIST "%BACKUP_DIR%" MKDIR "%BACKUP_DIR%"

:: Tao ten file theo dinh dang: CinemaDB_YYYY-MM-DD_HH-MM.sql
SET TIMESTAMP=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%-%TIME:~3,2%
SET TIMESTAMP=%TIMESTAMP: =0%
SET BACKUP_FILE=%BACKUP_DIR%\%DB_NAME%_%TIMESTAMP%.sql

:: Thuc hien dump
echo [%DATE% %TIME%] Bat dau sao luu %DB_NAME%...
%MYSQLDUMP% --host=%MYSQL_HOST% --port=%MYSQL_PORT% --user=%MYSQL_USER% --password=%MYSQL_PASS% ^
    --single-transaction --routines --triggers --events ^
    %DB_NAME% > "%BACKUP_FILE%"

IF %ERRORLEVEL% EQU 0 (
    echo [%DATE% %TIME%] Sao luu THANH CONG: %BACKUP_FILE%
) ELSE (
    echo [%DATE% %TIME%] LOI: Sao luu that bai! Ma loi: %ERRORLEVEL%
    EXIT /B %ERRORLEVEL%
)

:: --- Xoa file backup cu hon 30 ngay de tiet kiem dung luong ---
FORFILES /P "%BACKUP_DIR%" /S /M *.sql /D -30 /C "CMD /C DEL @PATH" 2>NUL
echo [%DATE% %TIME%] Da xoa cac file backup cu hon 30 ngay.

echo.
echo Hoan tat. Nhan phim bat ky de dong...
PAUSE
