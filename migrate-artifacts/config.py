host = "mombin.canonical.com"
sync_key_file = '/home/ubuntu/snapshots-sync/snapshots-sync'
move_key_file = '/home/ubuntu/snapshots-sync/snapshots-filemove'
sync_user = 'android-build-linaro'
move_user = 'android-build-linaro-trigger'
move_cmd = 'reshuffle-files'
jobs_path = '/var/lib/jenkins/jobs'
jobs_list = ['linaro-android*-release']
remote_prefix = 'android/.tmp/'
source_files = ['build/out/target/*/*/*.img',
                'build/out/target/*/*/*.tar.bz2',
                'build/out/target/*/*/MD5SUMS',
                'build/out/*.tar.bz2',
                'build/out/*.xml',
                'build/out/*_config',
                'build/out/lava-job-info',
                'build/out/download_and_build.sh']
remove = '(/archive/build/out)|(/builds)'
