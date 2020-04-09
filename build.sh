#!/bin/bash
set -e

APP="SA-cim_vladiator"
BUILD="build/$APP"
VER=$(grep version default/app.conf | cut -f2 -d=)
VER=${VER/ /}
TARBALL=${APP}-${VER}.tgz
echo "Building $APP ${VER}"
echo

# Clean existing build directory
[[ -d "$BUILD" ]] || rm -rf "$BUILD"
mkdir -p "$BUILD"

echo "Creating build into $BUILD"
cp -a ./*.md LICENSE bin appserver static default lookups metadata "$BUILD"
find "$BUILD" -name '*.py[co]' -delete
find "$BUILD" -name '.DS_Store' -delete

echo "Exporting to $TARBALL"
[[ -d "dist" ]] || mkdir dist


# MAC OSX undocumented hack to prevent creation of '._*' folders
export COPYFILE_DISABLE=1

(
cd build
tar -czvf "../dist/$TARBALL" "$APP"
)
echo "dist/$TARBALL" > .latest_release

echo
echo "New release:  dist/$TARBALL"
echo
echo "You can copy this file to your Splunk server or install it locally by running:"
echo
echo "    \$SPLUNK_HOME/bin/splunk install app dist/$TARBALL"

