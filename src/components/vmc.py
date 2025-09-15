from dataclasses import dataclass, asdict
import pulumi
from providers import VM, BlockDevice

@dataclass
class VMCInputs():
    num_block_devs: int = 1


class VMC(pulumi.ComponentResource):
    def __init__(self, name, props: VMCInputs, opts=None):
        super().__init__('custom:resource:VMC', name, asdict(props), opts)

        vm = VM(
            name="example_vm",
            opts=pulumi.ResourceOptions(parent=self)
        )
        """
        The BlockDevice resource requires the VM to be "off" before it can be created.
        Upon being deleted, it must also place the VM in an "off" state.
        """
        block_devices = []
        for _ in range(props.num_block_devs):
            block_device = BlockDevice(
                name="example_block_device",
                props={"uid": vm.uid},
                opts=pulumi.ResourceOptions(
                    parent=self,
                    depends_on=[vm]
                )
            )
            block_devices.append(block_device)

        self.vm = vm
        self.block_devices = block_devices

        self.register_outputs({
            "vm_id": vm.uid,
            "block_device_ids": [b.id for b in block_devices],
        })
