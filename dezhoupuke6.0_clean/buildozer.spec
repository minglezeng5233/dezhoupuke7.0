[app]

# 应用标题
title = 德州扑克3

# 包名（必须唯一）
package.name = texasholdem3

# 域名（反转的包名）
package.domain = org.poker

# 源代码目录
source.dir = .

# 主程序文件
source.main = main.py

# 支持的安卓版本
android.api = 33
android.minapi = 21
android.ndk = 25b

# SDK和NDK路径配置（避免自动下载）
# 使用系统已安装的Apache Ant
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
android.ant_path = /usr/share/ant

# 权限要求（简化权限要求）
android.permissions = INTERNET,VIBRATE

# 屏幕方向（竖屏优化）
orientation = portrait

# 全屏模式
fullscreen = 1

# 包含的模块
requirements = python3,kivy==2.2.1,openssl,requests,pyjnius

# 排除不必要的模块以减少包大小
android.blacklist_src = libgeos,libproj,libxml2,libxslt

# 优化性能设置
android.allow_backup = false
android.launch_mode = singleTop

# 包含的文件模式
include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,json

# 排除的文件模式
exclude_exts = .pyc,.pyo,.git,.gitignore,.DS_Store

# 图标文件
icon.filename = %(source.dir)s/icon.png

# 启动画面
presplash.filename = %(source.dir)s/splash.png

# 资源文件配置
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,json
source.include_patterns = *,sounds/*

# 应用版本
version = 3.0.0

# 版本代码（必须递增）
version.code = 1

# 作者信息
author = Poker Developer

# 应用描述
description = 德州扑克3 - 专业手游版，基于Kivy框架的移动端优化版本

# 日志级别
log_level = 2

# 构建配置
[buildozer]

# 日志级别
log_level = 2

# 工作目录
warn_on_root = 1

# Android配置
[app:android]

# 包含的架构（支持更多设备）
android.arch = armeabi-v7a,arm64-v8a

# 应用类别
android.meta_data = 

# 活动主题
android.theme = @android:style/Theme.NoTitleBar.Fullscreen

# 触摸优化
android.touchscreen_type = finger

# 屏幕尺寸支持
android.screen_size = normal,large,xlarge

# 屏幕密度支持
android.screen_density = mdpi,hdpi,xhdpi,xxhdpi

# 活动配置
android.entrypoint = org.poker.texasholdem3

# 应用类别（游戏）
android.app_category = game

# 支持多窗口模式
android.multiwindow_mode = none

# iOS配置（如果需要）
[app:ios]

# iOS版本要求
ios.deployment_target = 11.0

# iOS包标识符
ios.bundle_identifier = org.poker.texasholdem3

# 其他平台配置
[app:demo]

# 图形后端
[app:demo:graphics]

# 窗口设置
[app:demo:window]

# 输入设置
[app:demo:input]