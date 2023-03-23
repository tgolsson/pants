# Copyright 2023 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).
from textwrap import dedent

import pytest

from pants.build_graph.address import Address, AddressInput, ResolveError
from pants.core import register
from pants.core.target_types import GenericTarget
from pants.engine.addresses import Address
from pants.testutil.rule_runner import RuleRunner, engine_error
from pants.version import PANTS_SEMVER


def test_get_with_version():
    rule_runner = RuleRunner(aliases=[register.build_file_aliases()], target_types=[GenericTarget])

    rule_runner.write_files(
        {
            "BUILD": dedent(
                """\
                target(name=f'test{PANTS_VERSION}')
                """
            ),
        }
    )

    tgt = rule_runner.get_target(Address("", target_name=f"test{PANTS_SEMVER}"))
    assert tgt is not None


@pytest.mark.parametrize(
    "comparator,comparand",
    [
        (">", "2.0"),
        (">=", PANTS_SEMVER),
        ("==", PANTS_SEMVER),
        ("<=", PANTS_SEMVER),
        ("<", "3.0"),
        ("!=", "1.0"),
    ],
)
def test_get_version_comparable(comparator, comparand):
    rule_runner = RuleRunner(aliases=[register.build_file_aliases()], target_types=[GenericTarget])

    rule_runner.write_files(
        {
            "BUILD": dedent(
                f"""\
                if PANTS_VERSION {comparator} "{comparand}":
                    target(name=f'test{{PANTS_VERSION}}')
                """
            ),
        }
    )

    tgt = rule_runner.get_target(Address("", target_name=f"test{PANTS_SEMVER}"))
    assert tgt is not None


@pytest.mark.parametrize(
    "comparator,comparand",
    [
        (">", "2.0"),
        (">=", PANTS_SEMVER),
        ("==", PANTS_SEMVER),
        ("<=", PANTS_SEMVER),
        ("<", "3.0"),
        ("!=", "1.0"),
    ],
)
def test_get_version_not_comparable(comparator, comparand):
    rule_runner = RuleRunner(aliases=[register.build_file_aliases()], target_types=[GenericTarget])

    rule_runner.write_files(
        {
            "BUILD": dedent(
                f"""\
                condition = PANTS_VERSION {comparator} "{comparand}"
                if not condition:
                    target(name=f'test{{PANTS_VERSION}}')
                """
            ),
        }
    )

    with engine_error(ResolveError):
        rule_runner.get_target(Address("", target_name=f"test{PANTS_SEMVER}"))
