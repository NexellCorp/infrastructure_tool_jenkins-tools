# Keys should be in ../../../ansible-secrets-jenkins/jenkins-publish/
echo "ls
cd uploads/android/
put testfile
" | sftp -b - -i linaro-android-build-publish \
    linaro-android-build-publish@staging.snapshots.linaro.org

# I/O error during upload may mean disk full on the server
