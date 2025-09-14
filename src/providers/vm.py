"""A Python Pulumi program"""

from __future__ import annotations

from typing import override, Any

import pulumi
from pulumi import dynamic

from db import db


class VMProvider(dynamic.ResourceProvider):
    def configure(self, req: dynamic.ConfigureRequest) -> None:
        self.db_url = req.config.require("db_url")

    @override
    def check(self, _, news) -> dynamic.CheckResult:
        failures = []
        return dynamic.CheckResult(news, failures)

    @override
    def create(self, _) -> dynamic.CreateResult:
        pulumi.log.info("Creating VM")
        result = db(self.db_url).create("pending")
        pulumi.log.info(f"Created VM in DB: {result=}")
        return dynamic.CreateResult(
            id_=str(result["uid"]),
            outs={
                "uid": str(result["uid"]),
                "power_state": result["power_state"],
            }
        )


class VM(dynamic.Resource, module="vm", name="VM"):
    uid: pulumi.Output[str]
    power_state: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        _: dict[str, Any] = {},
        provider: dynamic.ResourceProvider | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            provider=provider or VMProvider(),
            name=name,
            props={
                "uid": None,
                "power_state": None,
            },
            opts=opts,
        )
