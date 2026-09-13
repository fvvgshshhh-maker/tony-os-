[app]
title = TonyOS
package.name = tonyos
package.domain = org.tonyos
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,kv
version = 1.0
requirements = python3,kivy,pyjnius,plyer
orientation = portrait
fullscreen = 0
android.permissions = CAMERA
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.copy_libs = 1
android.accept_sdk_license = True
[buildozer]
log_level = 2
warn_on_root = 1
