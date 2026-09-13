TONYOS ANDROID — REBUILT FOR GITHUB ACTIONS

This package contains a TonyOS Android project plus a GitHub Actions workflow.
You do not need Android Studio, WSL, Java, Python, or administrator access on Windows.

IMPORTANT:
Use the files in this package to replace the old files in your GitHub repository.
The new build uses current Buildozer/python-for-android settings:
- Android API 36
- minimum API 24
- Android NDK 29
- p4a develop branch
- Java 17
- Kivy only as the Python dependency

EASY GITHUB STEPS
1. Open your GitHub repository.
2. Replace buildozer.spec with the one in this folder.
3. Open .github/workflows/build-apk.yml and replace its contents with the one in this folder.
4. Commit both changes.
5. Open Actions.
6. Click "Build TonyOS APK".
7. Click "Run workflow".
8. Wait for the green check.
9. Open the completed run.
10. At the bottom, under Artifacts, download "TonyOS-APK".
11. Extract the ZIP and install the .apk on your Android phone.

The app requests CAMERA permission and saves photos for the Gallery.
