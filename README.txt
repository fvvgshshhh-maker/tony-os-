TONYOS ANDROID — EASY BUILD
===========================

This version includes a GitHub Actions builder, so you do NOT need admin rights,
WSL, Android Studio, Java, Buildozer, or Python installed on your own PC.

EASY METHOD
------------
1. Create a free GitHub account at https://github.com/ if you don't already have one.
2. Click the + button in the top-right and choose "New repository".
3. Name it: tonyos
4. Keep it Public or Private, then create the repository.
5. Open the new repository and choose "Add file" -> "Upload files".
6. Upload EVERYTHING from this folder, including the .github folder.
7. Click "Commit changes".
8. Open the "Actions" tab at the top of the repository.
9. Open "Build TonyOS APK".
10. Click "Run workflow" (or wait for the automatic build after your commit).
11. Wait for the build to finish with a green check.
12. Open that completed workflow run.
13. Scroll to "Artifacts" and download "TonyOS-APK".
14. Extract the downloaded ZIP. Inside is the TonyOS .apk.
15. Send the APK to your Android phone, open it, and install it.

The APK requests Android CAMERA permission for the TonyOS Camera app.
Photos captured by the Camera are stored in the app's TonyOS Pictures folder and
shown by the Gallery app.
