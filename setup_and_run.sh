#!/bin/bash
pulumi login --local

PULUMI_CONFIG_PASSPHRASE="" pulumi stack init development
PULUMI_CONFIG_PASSPHRASE="" pulumi config set db_url "some.db"

PULUMI_CONFIG_PASSPHRASE="" EXAMPLE_PROGRAM_NUMBER=1 pulumi up -y
PULUMI_CONFIG_PASSPHRASE="" EXAMPLE_PROGRAM_NUMBER=2 pulumi up -y
