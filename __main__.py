"""A Python Pulumi program"""

import pulumi

from providers import VM, BlockDevice, PowerState


def example_program_first_run():
    """
    The VM begins with some power_state which reflects the intended
    state of the VM at the end of all operations.

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
        props={"uid": vm.uid, "running_state": "on"},
        opts=pulumi.ResourceOptions(
            depends_on=[vm, block_device]
        )
    )

    pulumi.export("vm", vm)
    pulumi.export("block_device", block_device)
    pulumi.export("power_state", power_state)

if __name__ == "__main__":
    example_program_first_run()
