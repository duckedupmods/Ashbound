#!/bin/sh
# The real shader in a hidden window, no game: tools/fxpreview/run.sh -> tools/renders/fx_sheet.png
cd "$(dirname "$0")/../.." || exit 1
JAVA='E:/EFTest/jdk/jdk-21.0.12.1+1/bin/java'
G=~/.gradle/caches/modules-2/files-2.1/org.lwjgl
CP=""
for j in $(find $G/lwjgl/3.3.3 $G/lwjgl-glfw/3.3.3 $G/lwjgl-opengl/3.3.3 -name "*.jar" | grep -v "sources\|arm64\|x86\|linux\|macos"); do
	CP="$CP;$(cygpath -w "$j")"
done
"$JAVA" -cp "$CP" tools/fxpreview/FxPreview.java \
	src/main/resources/assets/ashbound/shaders/core/spell_fx.fsh \
	src/main/resources/assets/ashbound/shaders/core/gate.vsh \
	tools/renders/fx_sheet.png
