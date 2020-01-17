#!/usr/bin/env bash

# Environment settings for sbcAutoRun.py tool.
# The example data is for media plane install/upgrade.
# Verify the data below and update if needed.
# If data is correct, set environment running: source sbcAutoRunSetup.sh

# CBAM access data
export CBAM_CLIENT_ID=cbam_restapi
export CBAM_CLIENT_SECRET="0da68658-b9e4-4ef5-8f29-d6450e9f83c7"
export CBAM_HOST="https://10.76.172.8"

# Artifacts for install
export ARTIFACTS_DIR="/home/cbam/ArtifactsMedia"
export VNF_PACKAGE_FILE="Nokia_media_MGW_VNF_Package.zip"
export EXTENSION_FILE="Nokia_media_MGW.extensions.json"
export INSTANTIATE_FILE="Nokia_media_MGW.instantiate.json"

# Artifacts for nssu/issu
export UPGRADE_ARTIFACTS_DIR="/home/cbam/ArtifactsMedia/UPGRADE"
export UPGR_VNF_PACKAGE_FILE="Nokia_media_MGW_VNF_Package.zip"
export UPGR_EXTENSION_FILE="Nokia_media_MGW.extensions.json"

# Openstack RC File
export openstack_rc_file="/home/cbam/a799_SBC-openrc.sh"
source $openstack_rc_file
