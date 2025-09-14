"""A Python Pulumi program"""

import pulumi
import os

from providers import VM, BlockDevice, PowerState

example_program_number = int(os.environ["EXAMPLE_PROGRAM_NUMBER"])


def example_program_first_run():
    """
    The VM begins with 'pending' power_state.

    The VM is only responsible for creating the record in the remote system,
    but it never modifies it or acts on it beyond initial creation.

    For the purposes of this example, the VM is never updated or deleted.
    """
    vm = VM(name="example_vm")

    """
    The BlockDevice resource requires the VM to be "off" before it can be created.
    Upon being deleted, it must also place the VM in an "off" state.
    """
    block_device = BlockDevice(
        name="example_block_device",
        props={"uid": vm.uid},
        opts=pulumi.ResourceOptions(
            depends_on=[vm]
        )
    )

    """
    This PowerState resources is intended to always turn the VM on at the end of
    program execution.
    """
    power_state = PowerState(
        name="example_power_state",
        props={"uid": vm.uid, "power_state": "on"},
        opts=pulumi.ResourceOptions(
            depends_on=[vm, block_device]
        )
    )

    pulumi.export("vm", vm)
    pulumi.export("block_device", block_device)
    pulumi.export("power_state", power_state)


def example_program_second_run():
    """
    This program removes the BlockDevice resource, which requires the VM to be "off"
    """
    vm = VM(name="example_vm")

    """
    The BlockDevice resource requires the VM to be "off" before it can be created.
    Upon being deleted, it must also place the VM in an "off" state.

    BlockDevice is removed in this second run.
    """

    """
    This PowerState resources is intended to always turn the VM on at the end of
    program execution.
    """
    power_state = PowerState(
        name="example_power_state",
        props={"uid": vm.uid, "power_state": "on"},
        opts=pulumi.ResourceOptions(
            depends_on=[vm]
        )
    )

    pulumi.export("vm", vm)
    pulumi.export("power_state", power_state)

if __name__ == "__main__":
    if example_program_number == 1:
        example_program_first_run()
    elif example_program_number == 2:
        example_program_second_run()
    else:
        raise ValueError("EXAMPLE_PROGRAM_NUMBER must be set to either '1' or '2'")
