@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.未找到"sphinx-build"命令。请确保您已安装 Sphinx，然后将 SPHINXBUILD 环境变量设置为
	echo."sphinx-build"可执行文件的完整路径。或者，您可以将 Sphinx 目录添加到 PATH。
	echo.
	echo.如果您尚未安装 Sphinx，请从http://sphinx-doc.org/ 获取
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
