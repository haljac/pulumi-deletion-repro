import pulumi
import time
from functools import partial
from multiprocessing import Process, freeze_support
from pulumi import automation as auto
from components.vmc import VMC, VMCInputs
from providers import PowerState
from db import db
import os
import rich

os.environ["PULUMI_CONFIG_PASSPHRASE"] = ""
#example_program_number = int(os.environ["EXAMPLE_PROGRAM_NUMBER"])

debug = False
def debug_output(*args, **kwargs):
    rich.print(f"OUTPUT: {args=} {kwargs=}")


def debug_error(*args, **kwargs):
    rich.print(f"ERROR: {args=} {kwargs=}")

def print_output(output):
    rich.print(output)

def print_error(error):
    rich.print(f"[red]{error}[/red]")

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
        props=VMCInputs(num_block_devs=0),
        opts=pulumi.ResourceOptions(
            hooks=pulumi.ResourceHookBinding(
                before_update=[shutdown_vm],
                after_update=[]
            )
        )
    )
    pulumi.export("vmc", vmc)

def example_program_first_powerstate(vmc_stack_name):
    vm = pulumi.StackReference(vmc_stack_name).get_output("vmc")
    power_state = PowerState(
        name="example_power_state",
        props={
            "uid": vm["vm_id"],
            "power_state": "on",
        }
    
    )
    pulumi.export("power_state", power_state)

# def example_program_second_run():
#     vmc = VMC(
#         name="example_vmc",
#         props=VMCInputs(num_block_devs=0),
#         opts=pulumi.ResourceOptions(
#             hooks=pulumi.ResourceHookBinding(
#                 before_update=[shutdown_vm],
#                 after_update=[]
#             )
#         )
#     )
#     pulumi.export("vmc", vmc)


# def run_two():
#     target = "my-target"
#     app_name = "some-dummy-app"
#     project_settings = auto.ProjectSettings(
#         name=target,
#         runtime="python",
#         backend=auto.ProjectBackend(),
#     )
#     opts = auto.LocalWorkspaceOptions(project_settings=project_settings)
#     stack_name = auto.fully_qualified_stack_name("organization", target, app_name + "-2")
#     vmc_stack_name = auto.fully_qualified_stack_name("organization", target, app_name)
#     stack = auto.create_or_select_stack(
#         stack_name=stack_name,
#         project_name=target,
#         program=example_program_second_run,
#         opts=opts,
#     )
#     stack.set_config("db_url", auto.ConfigValue(value="some.db"))
#     stack.set_config("vmc_stack_name", auto.ConfigValue(value=vmc_stack_name))
#     stack.up(
#         on_output=debug_output if debug else print_output,
#         on_error=debug_error if debug else print_error,
#     )
if __name__ == "__main__":
    freeze_support()

    ##################################################
    # First run
    ##################################################
    target = "my-target"
    app_name = "some-dummy-app"
    project_settings = auto.ProjectSettings(
        name=target,
        runtime="python",
        backend=auto.ProjectBackend(),
    )
    opts = auto.LocalWorkspaceOptions(project_settings=project_settings)
    stack_name = auto.fully_qualified_stack_name("organization", target, app_name)
    stack = auto.create_or_select_stack(
        stack_name=stack_name,
        project_name=target,
        program=example_program_first_run,
        opts=opts,
    )
    stack.set_config("db_url", auto.ConfigValue(value="some.db"))
    p = Process(target=stack.up, kwargs={ "on_output": debug_output if debug else print_output, "on_error": debug_error if debug else print_error})
    p.start()
    p.join()

    ##################################################
    # Second run to change power state
    ##################################################
    target = "my-target"
    app_name = "some-dummy-app-powerstate"
    project_settings = auto.ProjectSettings(
        name=target,
        runtime="python",
        backend=auto.ProjectBackend(),
    )
    opts = auto.LocalWorkspaceOptions(project_settings=project_settings)
    stack_name = auto.fully_qualified_stack_name("organization", target, app_name)
    vmc_stack_name = auto.fully_qualified_stack_name("organization", target, "some-dummy-app")
    stack = auto.create_or_select_stack(
        stack_name=stack_name,
        project_name=target,
        program=partial(example_program_first_powerstate, vmc_stack_name),
        opts=opts,
    )
    stack.set_config("db_url", auto.ConfigValue(value="some.db"))
    stack.set_config("vmc_stack_name", auto.ConfigValue(value=vmc_stack_name))
    p = Process(target=stack.up, kwargs={ "on_output": debug_output if debug else print_output, "on_error": debug_error if debug else print_error})
    p.start()
    p.join()
