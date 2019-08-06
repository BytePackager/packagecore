##
# @file distributions.py
# @brief List of configurations for different distributions.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-08

# WARNING: Only use containers from trusted sources. Those listed here should
# only be 'official' containers from hub.docker.com.


# TODO: this should be editable and expandable by users in the future.

DATA = {
    "amazonlinux2017.03": {
        "dockerImage": "amazonlinux:2017.03",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.al.2017.03.{arch}.rpm"
    },
    "archlinux": {
        # there is no official arch linux docker image, so users will have
        # to specify one
        "dockerImage": None,
        "packageType": "pkgbuild",
        "formatString": "{name}-{version}-{release}-{arch}.pkg.tar.xz"
    },
    "centos6.9": {
        "dockerImage": "centos:6.9",
        "packageType": "rpm-yum",
        # centos 6 doesn't generate a 'centos' as part of the arch
        "formatString": "{name}-{version}-{release}.el6.9.centos.{arch}.rpm"
    },
    "centos7.0": {
        "dockerImage": "centos:7.0.1406",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.0.centos.{arch}.rpm"
    },
    "centos7.1": {
        "dockerImage": "centos:7.1.1503",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.1.centos.{arch}.rpm"
    },
    "centos7.2": {
        "dockerImage": "centos:7.2.1511",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.2.centos.{arch}.rpm"
    },
    "centos7.3": {
        "dockerImage": "centos:7.3.1611",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.3.centos.{arch}.rpm"
    },
    "centos7.4": {
        "dockerImage": "centos:7.4.1708",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.4.centos.{arch}.rpm"
    },
    "centos7.5": {
        "dockerImage": "centos:7.5.1804",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.5.centos.{arch}.rpm"
    },
    "centos7.6": {
        "dockerImage": "centos:7.6.1810",
        "packageType": "rpm-yum",
        "formatString": "{name}-{version}-{release}.el7.6.centos.{arch}.rpm"
    },
    "debian8": {
        "dockerImage": "debian:jessie",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_debian8.{arch}.deb"
    },
    "debian9": {
        "dockerImage": "debian:stretch",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_debian9.{arch}.deb"
    },
    "debian10": {
        "dockerImage": "debian:buster",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_debian10.{arch}.deb"
    },
    "fedora22": {
        "dockerImage": "fedora:22",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc22.{arch}.rpm"
    },
    "fedora23": {
        "dockerImage": "fedora:23",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc23.{arch}.rpm"
    },
    "fedora24": {
        "dockerImage": "fedora:24",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc24.{arch}.rpm"
    },
    "fedora25": {
        "dockerImage": "fedora:25",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc25.{arch}.rpm"
    },
    "fedora26": {
        "dockerImage": "fedora:26",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc26.{arch}.rpm"
    },
    "fedora27": {
        "dockerImage": "fedora:27",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc27.{arch}.rpm"
    },
    "fedora28": {
        "dockerImage": "fedora:28",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc28.{arch}.rpm"
    },
    "fedora29": {
        "dockerImage": "fedora:29",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc29.{arch}.rpm"
    },
    "fedora30": {
        "dockerImage": "fedora:30",
        "packageType": "rpm-dnf",
        "formatString": "{name}-{version}-{release}.fc30.{arch}.rpm"
    },
    "opensuse42.3": {
        "dockerImage": "opensuse/leap:42.3",
        "packageType": "rpm-zypper",
        "formatString": "{name}-{version}-{release}.opensuse42.3.{arch}.rpm"
    },
    "opensuse15.0": {
        "dockerImage": "opensuse/leap:15.0",
        "packageType": "rpm-zypper",
        "formatString": "{name}-{version}-{release}.opensuse15.0.{arch}.rpm"
    },
    "opensuse15.1": {
        "dockerImage": "opensuse/leap:15.1",
        "packageType": "rpm-zypper",
        "formatString": "{name}-{version}-{release}.opensuse15.1.{arch}.rpm"
    },
    "ubuntu14.04": {
        "dockerImage": "ubuntu:14.04",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_ubuntu14.04.{arch}.deb"
    },
    "ubuntu16.04": {
        "dockerImage": "ubuntu:16.04",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_ubuntu16.04.{arch}.deb"
    },
    "ubuntu16.10": {
        "dockerImage": "ubuntu:16.10",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_ubuntu16.10.{arch}.deb"
    },
    "ubuntu17.04": {
        "dockerImage": "ubuntu:17.04",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_ubuntu17.04.{arch}.deb"
    },
    "ubuntu17.10": {
        "dockerImage": "ubuntu:17.10",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_ubuntu17.10.{arch}.deb"
    },
    "ubuntu18.04": {
        "dockerImage": "ubuntu:18.04",
        "packageType": "debian",
        "formatString": "{name}_{version}-{release}_ubuntu18.04.{arch}.deb"
    },
}
