[app]
title = KivyTest
package.name = kivytest
package.domain = org.jjtrig
version = 0.1.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy
orientation = portrait

android.sdk = 33
android.ndk = 25b
android.sdk_build_tools = 33.0.0
android.minapi = 21
android.accept_sdk_license = True
android.arch = arm64-v8a
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE
android.modules = org.kivy.camera
android.logcat_filters = *:S python:D