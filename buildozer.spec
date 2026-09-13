[app]
title = TonyOS
package.name = tonyos
package.domain = org.tonyos
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,kv
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = CAMERA
android.api = 36
android.minapi = 24
android.ndk = 29
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.copy_libs = True
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 0
