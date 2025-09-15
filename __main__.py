"""A Python Pulumi program"""

import pulumi
import os

import time
from components.vmc import VMC, VMCInputs
from db import db

example_program_number = int(os.environ["EXAMPLE_PROGRAM_NUMBER"])

def shutdown_vm(args: pulumi.ResourceHookArgs):
    pulumi.log.info(f"({time.monotonic()})[hook] shutdown_vm {args.old_inputs=}")
    pulumi.log.info(f"({time.monotonic()})[hook] shutdown_vm {args.new_inputs=}")
    pulumi.log.info(f"({time.monotonic()})[hook] before_update")
    vm_id = (args.old_outputs or {}).get("vm_id")
    old_n_block_devs = getattr(args, "old_inputs", {}).get("num_block_devs", 0)
    new_n_block_devs = getattr(args, "new_inputs", {}).get("num_block_devs", 0)
    if old_n_block_devs > new_n_block_devs:
        pulumi.log.info(f"({time.monotonic()})[hook] shutting down VM because block device count is decreasing")
        db("some.db").update(vm_id, "off")
        time.sleep(2)

def example_program_first_run():
    vmc = VMC(
        name="example_vmc",
        props=VMCInputs(num_block_devs=1),
        opts=pulumi.ResourceOptions(
            hooks=pulumi.ResourceHookBinding(
                before_update=[shutdown_vm],
                after_update=[]
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
                before_update=[shutdown_vm],
                after_update=[]
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
