@echo off
ECHO ----------------------------------------
echo Creating Confluence Build Folder
IF Exist ..\..\project\Win32BuildSetup\BUILD_WIN32\application\addons\skin.fusion.confluence rmdir ..\..\project\Win32BuildSetup\BUILD_WIN32\application\addons\skin.fusion.confluence /S /Q
md ..\..\project\Win32BuildSetup\BUILD_WIN32\application\addons\skin.fusion.confluence\media\

Echo .svn>exclude.txt
Echo Thumbs.db>>exclude.txt
Echo Desktop.ini>>exclude.txt
Echo dsstdfx.bin>>exclude.txt
Echo build.bat>>exclude.txt
Echo \skin.fusion.confluence\media\>>exclude.txt
Echo exclude.txt>>exclude.txt

ECHO ----------------------------------------
ECHO Creating XBT File...
START /B /WAIT ..\..\Tools\TexturePacker\TexturePacker -dupecheck -input media -output ..\..\project\Win32BuildSetup\BUILD_WIN32\application\addons\skin.fusion.confluence\media\Textures.xbt

ECHO ----------------------------------------
ECHO XBT Texture Files Created...
ECHO Building Skin Directory...
xcopy "..\skin.fusion.confluence" "..\..\project\Win32BuildSetup\BUILD_WIN32\application\addons\skin.fusion.confluence" /E /Q /I /Y /EXCLUDE:exclude.txt

del exclude.txt
