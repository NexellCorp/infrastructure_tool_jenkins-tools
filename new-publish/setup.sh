#!/bin/bash
set -e

publish_home=/mnt/publish

# Append content to a file if grep test fails
function add_if_absent() {
    file=$1
    exists_regexp=$2
    to_add=$3
    if grep -q -E "$exists_regexp" "$file"; then
        echo "Warning $file matched $exists_regexp, adding new content skipped"
        return
    fi
    echo "$to_add" >>$file
}

# Comment out (#) a line if it matches regexp
function comment_if_present() {
    file=$1
    regexp=$2
    awk "\
/$regexp/ {print \"#\" \$0; next; }
    { print }
" $file > $file.tmp
    mv $file.tmp $file
}

function setup_accounts() {

    mkdir -p $publish_home

    groupadd publish || true

    useradd \
        --comment "Publishing - transfer user" \
        --home $publish_home \
        --gid publish \
        -M \
        --no-user-group \
        publish-copy || true

    useradd \
        --comment "Publishing - finalization user" \
        --home $publish_home \
        --gid publish \
        -M \
        --no-user-group \
        publish-trigger || true

    # Home dir must be owned by root for ssh ChrootDirectory to work
    chown root.root $publish_home
    chmod 755 $publish_home

    # Actual uploads will happen to this dir
    mkdir -p $publish_home/uploads
    # publish-copy should have write access there, publish-trigger
    # generally only read (cleanup can be handled by cronjob)
    chown publish-copy.publish $publish_home/uploads
    chmod 755 $publish_home/uploads
}


function setup_sshd_config() {
    sshd_config=/etc/ssh/sshd_config
#    sshd_config=sshd_config
    if [ ! -f $sshd_config.before-new-pub ]; then
        # Capture pristine config for rollback
        cp $sshd_config $sshd_config.before-new-pub
    fi

    add_if_absent $sshd_config "^AuthorizedKeysFile /etc/ssh/user-authorized-keys/%u" "\
AuthorizedKeysFile /etc/ssh/user-authorized-keys/%u
AuthorizedKeysFile2 /dev/null"

    comment_if_present $sshd_config "^Subsystem sftp"
    add_if_absent $sshd_config "^Subsystem sftp internal-sftp" "Subsystem sftp internal-sftp"

    add_if_absent $sshd_config "^Match User publish-copy" "\
Match User publish-copy
       ChrootDirectory $publish_home
       ForceCommand    internal-sftp
       AllowTcpForwarding    no
       X11Forwarding         no
"
}

function setup_ssh_keys() {
    mkdir -p /etc/ssh/user-authorized-keys/
    # Move only real file, don't do this for symlink
    if [ ! -L $HOME/.ssh/authorized_keys ]; then
        echo "Moving current account's authorized_keys to /etc/ssh/user-authorized-keys/"
        cp $HOME/.ssh/authorized_keys /etc/ssh/user-authorized-keys/$SUDO_USER
        rm $HOME/.ssh/authorized_keys
        ln -s /etc/ssh/user-authorized-keys/$SUDO_USER $HOME/.ssh/authorized_keys
    fi
    # Unlike when reside in ~/.ssh/, in /etc/ssh/... auth keys must be readable enough,
    # or won't be picked up by sshd => login lockout.
    chmod 644 /etc/ssh/user-authorized-keys/$SUDO_USER

    mkdir -p ~/snapshots-sync3
    if [ ! -f ~/snapshots-sync3/publish-copy ]; then
        ssh-keygen -t rsa -N "" -f ~/snapshots-sync3/publish-copy
    fi
    if [ ! -f ~/snapshots-sync3/publish-trigger ]; then
        ssh-keygen -t rsa -N "" -f ~/snapshots-sync3/publish-trigger
    fi


    echo -n 'command="/usr/lib/sftp-server",no-pty,no-port-forwarding,no-X11-forwarding,no-agent-forwarding ' \
        >/etc/ssh/user-authorized-keys/publish-copy
    pubkey=$(cat ~/snapshots-sync3/publish-copy.pub)
    add_if_absent /etc/ssh/user-authorized-keys/publish-copy "^$pubkey" "$pubkey"

    echo -n 'command="/home/ubuntu/new-publish/utils/new-publish/trigger ${SSH_ORIGINAL_COMMAND#* }",no-pty,no-port-forwarding,no-X11-forwarding,no-agent-forwarding ' \
        >/etc/ssh/user-authorized-keys/publish-trigger
    pubkey=$(cat ~/snapshots-sync3/publish-trigger.pub)
    add_if_absent /etc/ssh/user-authorized-keys/publish-trigger "^$pubkey" "$pubkey"
}

setup_accounts
# Setup new ssh keys structure first, or there's a chance of SSH lock-out
setup_ssh_keys
setup_sshd_config
