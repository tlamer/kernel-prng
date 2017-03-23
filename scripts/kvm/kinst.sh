#!/bin/bash

err() {
    echo "$@" 1>&2
}

debug() {
    [[ $DEBUG -eq 1 ]] && "$@" || :
}

function ask {
    while true; do

        if [ "${2:-}" = "Y" ]; then
            prompt="Y/n"
            default=Y
        elif [ "${2:-}" = "N" ]; then
            prompt="y/N"
            default=N
        else
            prompt="y/n"
            default=
        fi

        # Ask the question
        read -p "$1 [$prompt] " REPLY

        # Default?
        if [ -z "$REPLY" ]; then
            REPLY=$default
        fi

        # Check if the reply is valid
        case "$REPLY" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}

kernel_install() {
    # function for kernel installation
    local target="$1"
    local ver="$2"
    local bzimage="/boot/vmlinuz-${ver}"
    local ramfs="/boot/initramfs-${ver}.img"
    local bzimagelnk="/boot/vmlinuz-devel"
    local ramfslnk="/boot/initramfs-devel"

    debug echo "target: $target"
    debug echo "ver: $ver"
    debug echo "bzimage: $bzimage"
    debug echo "ramdisk: $ramfs"
    debug echo "bzimage symlink: $bzimagelnk"
    debug echo "ramdisk symlink: $ramfslnk"

    printf "Installing modules\n"
    make modules_install > /dev/null
    [[ $? -ne 0 ]] && { err "make modules_install has failed." ; return 5; }

    printf "\nInstall kernel\n"
    cp -v "$target/arch/x86_64/boot/bzImage" "$bzimage"
    [[ $? -ne 0 ]] && { err "Kernel installation has failed." ; return 6; }

    printf "\nGenerate ramdisk\n"
    mkinitcpio -k "$ver" -c "/etc/mkinitcpio.conf" -g "$ramfs"
    [[ $? -ne 0 ]] && { err "Failed to generate ramdisk." ; return 7; }

    [[ -e $bzimagelnk ]] && rm -v "$bzimagelnk"
    [[ -e $ramfslnk ]] && rm -v "$ramfslnk"

    ln -v -s "$bzimage" "$bzimagelnk"
    ln -v -s "$ramfs" "$ramfslnk"

#    printf "\n Backup and generate grub.cfg\n"
#    cp -v "/boot/grub/grub.cfg" "/boot/grub/grub.cfg.bak"
#    grub-mkconfig -o "/boot/grub/grub.cfg"
#    [[ $? -ne 0 ]] && { err "Failed to generate grub.cfg." ; exit 8; }

}

main() {
    # check if running as root
    if [[ $EUID -ne 0 ]] ; then
        err "This script has to be run as root."
        exit 3
    fi

    # get target parameter
    if [[ $# -eq 1 ]] ; then
        TARGET="$(readlink -f "$1")"
    else
        err "Specify target directory with compiled kernel."
        exit 2
    fi

    # sanity checks
    if [[ -d $TARGET ]] ; then
        cd "$TARGET"
    else
        err "Could not cd to $TARGET"
        exit 1
    fi

    # get version string
    VER="$(make kernelrelease)"
    [[ -z $VER ]] && { err "Could not get kernel version string." ; exit 4; }

    ask "Install linux-${VER}?" Y || exit ;

    if [[ -d "/lib/modules/${VER}" || -e "/boot/vmlinuz-${VER}" || -e "/boot/initramfs-${VER}.img" ]] ; then
        ask "It seems that kernel ${VER} is already installed, continue?" N || exit
    fi

    # kernel install
    kernel_install "$TARGET" "$VER"
}

main "$@"
exit "$?"

