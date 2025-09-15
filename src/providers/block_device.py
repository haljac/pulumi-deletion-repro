"""A Python Pulumi program"""
import time

from typing import Any, Mapping, override

import pulumi
from pulumi import dynamic



class BlockDeviceProvider(dynamic.ResourceProvider):
    def configure(self, req: dynamic.ConfigureRequest) -> None:
        self.db_url = req.config.require("db_url")


    @override
    def check(self, _, news) -> dynamic.CheckResult:
        failures = []
        return dynamic.CheckResult(news, failures)


    @override
    def create(self, props) -> dynamic.CreateResult:
        return dynamic.CreateResult(
            id_=props["uid"],
            outs={},
        )


    @override
    def delete(self, id_: str, _) -> None:
        time.sleep(2)
        pulumi.log.info(f"({time.monotonic()})[BlockDeviceProvider] delete {id_=}")
        # db(self.db_url).update(id_, "off")


class BlockDevice(dynamic.Resource, module="block_device", name="BlockDevice"):
    uid: pulumi.Input[str]
    def __init__(
        self,
        name: str,
        props: Mapping[str, Any] = {},
        provider: dynamic.ResourceProvider | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            provider=provider or BlockDeviceProvider(),
            name=name,
            props=props,
            opts=opts,
        )
