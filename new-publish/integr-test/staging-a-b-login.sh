# Keys should be in ../../../ansible-secrets-jenkins/jenkins-publish/
echo "================="
# Expected result: successful connection, message about "sftp only"
ssh -i linaro-android-build-publish \
    linaro-android-build-publish@staging.snapshots.linaro.org
echo "================="
# Expected result: successful connection, usage from "publish_to_snapshots.py"
ssh -i linaro-android-build-publish-trigger \
    linaro-android-build-publish-trigger@staging.snapshots.linaro.org
echo "================="
