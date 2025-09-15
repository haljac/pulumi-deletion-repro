"""A Python Pulumi program"""

import pulumi
import os
import time
from db import db

from components.vmc import VMC, VMCInputs

example_program_number = int(os.environ["EXAMPLE_PROGRAM_NUMBER"])

def shutdown_vm(args: pulumi.ResourceHookArgs):
    pulumi.log.info(f"({time.monotonic()})[hook] before_update")
    vm_id = (args.old_outputs or {}).get("vm_id")
    old_block_device_ids = getattr(args, "old_outputs", {}).get("block_device_ids", [])
    new_block_device_ids = getattr(args, "new_inputs", {}).get("block_device_ids", [])
    if len(old_block_device_ids) > len(new_block_device_ids):
        pulumi.log.info(f"({time.monotonic()})[hook] shutting down VM because block device count is decreasing")
        db("some.db").update(vm_id, "off")
        time.sleep(2)

def start_vm(args: pulumi.ResourceHookArgs):
    pulumi.log.info(f"({time.monotonic()})[hook] after_delete")
    vm_id = (args.old_outputs or {}).get("vm_id")
    db("some.db").update(vm_id, "on")

shutdown_vm_hook = pulumi.ResourceHook(name="shutdown_vm_hook", func=shutdown_vm)
start_vm_hook = pulumi.ResourceHook(name="start_vm_hook", func=start_vm)


def example_program_first_run():
    vmc = VMC(
        name="example_vmc",
        props=VMCInputs(num_block_devs=1),
        opts=pulumi.ResourceOptions(
            hooks=pulumi.ResourceHookBinding(
                before_update=[shutdown_vm_hook],
                after_update=[start_vm_hook]
            )
        )
    )
    pulumi.export("vmc", vmc)


def example_program_second_run():
    vmc = VMC(
        name="example_vmc",
        props=VMCInputs(num_block_devs=0),
        opts=pulumi.ResourceOptions(
            hooks=pulumi.ResourceHookBinding(
                before_update=[shutdown_vm_hook],
                after_update=[start_vm_hook]
            )
        )
    )
    pulumi.export("vmc", vmc)

if __name__ == "__main__":
    if example_program_number == 1:
        example_program_first_run()
    elif example_program_number == 2:
        example_program_second_run()
    else:
        raise ValueError("EXAMPLE_PROGRAM_NUMBER must be set to either '1' or '2'")
