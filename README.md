# Flutter3_Reflutter_APK
This script automates the process of fixing Flutter-based APKs that lack an x86 build of libflutter.so (common issue when running on Genymotion or x86 emulators).  

The result is a fully patched, aligned, and signed APK that includes an x86-compatible, making it run smoothly on Genymotion and x86 Android emulators.

# Requirement: 
### Apktool (https://github.com/iBotPeaches/Apktool)
### Uber APK Signer (https://github.com/patrickfav/uber-apk-signer) 
### Reflutter → pip install reflutter

# Set Path 
### APKTOOL = r"path\apktool.jar" 
### UBER_SIGNER = r"path\uber-apk-signer.jar"

# Run
### python fix.py path\to\your.apk
