echo "========================================================"
echo "This will upgrade Jenkins and Jenkins plugins to the versions"
echo "as maitained in Ansible configuration."
echo "1. This means DOWNTIME for a Jenkins server, all running builds"
echo "   will be ABORTED."
echo "2. This may lead to DATA LOSS if you make unvalidated upgrade."
echo "3. This may lead to IRRECOVERABLE SERVICE LOSS if you mis-type"
echo "   or mis-think something."
echo "========================================================"

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <jenkins-host> <Linaro.account>"
    echo "where <jenkins-host> is one of ci.linaro.org, rdk-ci.linaro.org, etc."
    echo "(see hosts-prod for complete list)"
    exit 1
fi

echo
echo "Please read the warning above and type YES if you are sure you want to proceed."

read input

if [ "$input" != "YES" ]; then
    echo "Operation cancelled"
    exit 0
fi

time ansible-playbook -i hosts-prod -l "$1" --user "$2" --ask-sudo-pass jenkins.yml --tags jenkins-install
