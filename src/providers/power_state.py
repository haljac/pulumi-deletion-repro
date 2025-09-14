"""A Python Pulumi program"""
from __future__ import annotations

from typing import Any, Mapping, override

import pulumi
from pulumi import dynamic

from db import db


class PowerStateProvider(dynamic.ResourceProvider):
    def configure(self, req: dynamic.ConfigureRequest) -> None:
        self.db_url = req.config.require("db_url")


    @override
    def check(self, _, news) -> dynamic.CheckResult:
        failures = []
        return dynamic.CheckResult(news, failures)


    @override
    def create(self, props) -> dynamic.CreateResult:
        result = db(self.db_url).update(props["uid"], props.get("power_state", "on"))
        return dynamic.CreateResult(
            id_=result["uid"],
            outs={
                "uid": str(props["uid"]),
                "power_state": result["power_state"],
            }
        )


    @override
    def diff(self, id_: str, _, news) -> dynamic.DiffResult:
        replaces = []
        result = db(self.db_url).read(id_)
        changes = result["power_state"] != news["power_state"]
        if changes:
            replaces.append("power_state")

        return dynamic.DiffResult(
            changes=changes,
            replaces=replaces,
        )


    @override
    def update(self, id_: str, _, news) -> dynamic.UpdateResult:
        result = db(self.db_url).update(id_, news.get("power_state", "on"))
        return dynamic.UpdateResult(
            outs={
                "uid": str(id_),
                "power_state": result["power_state"],
            }
        )


class PowerState(dynamic.Resource, module="power_state", name="PowerState"):
    uid: pulumi.Input[str]
    power_state: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        props: Mapping[str, Any],
        provider: dynamic.ResourceProvider | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            provider=provider or PowerStateProvider(),
            name=name,
            props=props,
            opts=opts,
        )
