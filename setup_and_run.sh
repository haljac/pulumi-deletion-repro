#!/bin/bash
pulumi login --local

PULUMI_CONFIG_PASSPHRASE="" pulumi stack init development
PULUMI_CONFIG_PASSPHRASE="" pulumi config set db_url "some.db"

PULUMI_CONFIG_PASSPHRASE="" EXAMPLE_PROGRAM_NUMBER=1 pulumi up -y
PULUMI_CONFIG_PASSPHRASE="" EXAMPLE_PROGRAM_NUMBER=2 pulumi up -y

vm_power_state=$(sqlite3 some.db 'SELECT power_state FROM vms WHERE uid = 1;')
if [ "$vm_power_state" == "on" ]; then
    echo "VM is running as expected. RunningStateProvider restarted VM successfully."
else
    echo "Unexpected VM power state: $vm_power_state"
    exit 1
fi

rm -rf ~/.pulumi
rm some.db
