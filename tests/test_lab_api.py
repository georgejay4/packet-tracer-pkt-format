#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 aacanadaa
# This file is part of packet-tracer-pkt-format (GPL-3.0-or-later).
"""Tests for tools/lab_api.py -- device-name collisions and seed pruning.

The seed (tools/network_seed.xml) contributes pre-existing devices (SW1, R1,
R2, PC-A, PC-B, Server, Power Distribution Device0).  Naming a generated
device after one of them used to silently produce a duplicate; `add_device()`
now refuses by default and `prune_seed_devices()` drops the inherited devices
for a clean workspace.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))  # pt9 (same convention as tests/test_pt9.py)
TOOLS = REPO / "tools"


def _load_lab_api():
    spec = importlib.util.spec_from_file_location("lab_api", TOOLS / "lab_api.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lab_api = _load_lab_api()

# names the shipped seed is known to contribute (the original collision report)
SEED_NAMES = {"SW1", "R1", "R2", "PC-A", "PC-B", "Server", "Power Distribution Device0"}


@pytest.fixture(scope="module")
def templates():
    return lab_api.load_templates(str(TOOLS / "device_templates.json"))


@pytest.fixture()
def lab(templates):
    models, modules = templates
    return lab_api.Lab(str(TOOLS / "network_seed.xml"), models, modules)


def _device_count(lab) -> int:
    return len(lab.devs.findall("DEVICE"))


# --------------------------------------------------------------------------- #
# device_names()
# --------------------------------------------------------------------------- #
def test_device_names_lists_seed_devices(lab):
    names = lab.device_names()
    assert len(names) == _device_count(lab)
    assert SEED_NAMES.issubset(set(names)), f"seed names missing from {names}"


def test_device_names_includes_added_devices(lab):
    before = set(lab.device_names())
    lab.add_device("2911", "R9")
    after = set(lab.device_names())
    assert after - before == {"R9"}


def test_unnamed_routers_and_switches_use_default_convention(lab):
    lab.prune_seed_devices()
    router1 = lab.add_device("2911")
    router2 = lab.add_device("ISR4331")
    switch1 = lab.add_device("2960-24TT")
    switch2 = lab.add_device("3560-24PS")

    assert [lab._els[sid].findtext("ENGINE/NAME")
            for sid in (router1, router2, switch1, switch2)] == [
                "R1", "R2", "SW1", "SW2",
            ]


def test_default_names_skip_names_already_in_seed(lab):
    router = lab.add_device("2911")
    switch = lab.add_device("2960-24TT")

    assert lab._els[router].findtext("ENGINE/NAME") == "R3"
    assert lab._els[switch].findtext("ENGINE/NAME") == "SW2"


def test_explicit_device_name_overrides_convention(lab):
    router = lab.add_device("2911", "EDGE-RTR")
    switch = lab.add_device("2960-24TT", "DIST-SW")

    assert lab._els[router].findtext("ENGINE/NAME") == "EDGE-RTR"
    assert lab._els[switch].findtext("ENGINE/NAME") == "DIST-SW"


def test_generated_ports_use_unique_bia_without_ios_mac_overrides(lab):
    router = lab._els[lab.add_device("2911", "R9")]
    switch = lab._els[lab.add_device("2960-24TT", "SW9")]

    port_macs = [
        (port.findtext("MACADDRESS"), port.findtext("BIA"))
        for device in (router, switch)
        for port in device.find("ENGINE").iter("PORT")
        if port.findtext("MACADDRESS") or port.findtext("BIA")
    ]
    active_macs = [mac for mac, _ in port_macs]
    burned_in = [bia for _, bia in port_macs]

    assert all(mac == bia for mac, bia in port_macs)
    assert len(active_macs) == len(set(active_macs))
    assert len(burned_in) == len(set(burned_in))


def test_installed_module_ports_use_bia_as_default_mac(lab):
    device_id = lab.add_device("2911", "R9")
    lab.modules["TestModule"] = (
        "<SLOT><TYPE>eInterfaceCard</TYPE><MODULE><TYPE>eInterfaceCard</TYPE>"
        "<MODEL>TestModule</MODEL><PORT><TYPE>eCopperFastEthernet</TYPE>"
        "<MACADDRESS>0000.0000.0001</MACADDRESS>"
        "<BIA>0000.0000.0002</BIA></PORT></MODULE></SLOT>"
    )

    lab.install_module(device_id, "TestModule", slot=1)

    module = next(
        module for module in lab._els[device_id].findall(".//MODULE")
        if module.findtext("MODEL") == "TestModule"
    )
    module_port = module.find("PORT")
    assert module_port is not None
    assert module_port.findtext("MACADDRESS") == module_port.findtext("BIA")


def test_unnamed_non_network_device_requires_name(lab):
    with pytest.raises(ValueError, match="device name is required"):
        lab.add_device("PC-PT")


def test_save_sets_hostnames_and_removes_domain_name_commands(lab, monkeypatch):
    lab.add_device(
        "2911", "R9",
        ios_config=[
            "hostname R9",
            "ip domain-name old.example",
            "no ip domain-name",
            "end",
        ],
    )
    encoded = {}
    monkeypatch.setattr(
        lab_api.pt9, "encode",
        lambda _path, xml, _fmt: encoded.update(xml=xml),
    )

    lab.save("unused.pkt")

    root = ET.fromstring(encoded["xml"])
    devices = root.find("NETWORK/DEVICES").findall("DEVICE")
    for device in devices:
        engine = device.find("ENGINE")
        model = engine.find("TYPE").get("model", "")
        if lab_api.kind_for_model(model) in lab_api._IOS_DEVICE_KINDS:
            display_name = engine.findtext("NAME")
            hostnames = [
                (line.text or "").strip()
                for line in engine.findall("RUNNINGCONFIG/LINE")
                if (line.text or "").strip().lower().startswith("hostname ")
            ]
            commands = [
                line.text for line in engine.findall("RUNNINGCONFIG/LINE")
                if re.match(
                    r"(?:no\s+)?ip domain-name(?:\s|$)",
                    (line.text or "").strip(),
                    re.I,
                )
            ]
            assert hostnames == [f"hostname {display_name}"]
            assert commands == []
        else:
            assert not any(
                (line.text or "").strip().lower().startswith("ip domain-name")
                for line in engine.findall("RUNNINGCONFIG/LINE")
            )


# --------------------------------------------------------------------------- #
# add_device() collision detection
# --------------------------------------------------------------------------- #
def test_add_device_rejects_seed_name(lab):
    n_before = _device_count(lab)
    with pytest.raises(ValueError, match="already in use") as exc:
        lab.add_device("2911", "SW1")
    assert "SW1" in str(exc.value)
    # a rejected name must not leave a half-added device behind
    assert _device_count(lab) == n_before
    assert "SW1(1)" not in lab.device_names()


def test_add_device_rejects_duplicate_generated_name(lab):
    lab.add_device("2911", "R9")
    with pytest.raises(ValueError, match="already in use"):
        lab.add_device("2911", "R9")
    assert lab.device_names().count("R9") == 1


def test_add_device_rejects_name_added_by_suffixing(lab):
    lab.add_device("2911", "R9")
    lab.add_device("2911", "R9", on_name_conflict="suffix")  # -> R9(1)
    with pytest.raises(ValueError, match="already in use"):
        lab.add_device("2911", "R9(1)")


def test_add_device_suffix_auto_renames(lab):
    sid0 = lab.add_device("2911", "R9")
    sid1 = lab.add_device("2911", "R9", on_name_conflict="suffix")
    sid2 = lab.add_device("2911", "R9", on_name_conflict="suffix")
    assert len({sid0, sid1, sid2}) == 3
    names = lab.device_names()
    assert names.count("R9") == 1
    assert names.count("R9(1)") == 1
    assert names.count("R9(2)") == 1


def test_add_device_suffix_on_seed_name(lab):
    lab.add_device("2960-24TT", "SW1", on_name_conflict="suffix")
    names = lab.device_names()
    assert "SW1(1)" in names
    assert names.count("SW1") == 1  # the seed's own SW1, untouched


def test_add_device_rejects_unknown_conflict_policy(lab):
    with pytest.raises(ValueError, match="on_name_conflict"):
        lab.add_device("2911", "R9", on_name_conflict="rename-silently")


# --------------------------------------------------------------------------- #
# prune_seed_devices()
# --------------------------------------------------------------------------- #
def test_prune_seed_devices_removes_only_the_seed(lab):
    seed = set(lab.device_names())
    lab.add_device("2911", "R9")
    lab.add_device("PC-PT", "PC9")
    removed = lab.prune_seed_devices()
    assert set(removed) == seed
    assert lab.device_names() == ["R9", "PC9"]
    assert _device_count(lab) == 2


def test_prune_seed_devices_is_idempotent(lab):
    lab.add_device("2911", "R9")
    lab.prune_seed_devices()
    assert lab.prune_seed_devices() == []
    assert lab.device_names() == ["R9"]


def test_prune_seed_devices_frees_seed_names(lab):
    lab.prune_seed_devices()
    lab.add_device("2911", "SW1")  # no ValueError any more
    assert "SW1" in lab.device_names()


def test_drop_seed_devices_is_an_alias(lab):
    assert lab_api.Lab.drop_seed_devices is lab_api.Lab.prune_seed_devices
    lab.add_device("2911", "R9")
    assert set(lab.drop_seed_devices()) == SEED_NAMES
    assert lab.device_names() == ["R9"]


def test_prune_seed_devices_removes_links_to_seed_devices(lab):
    seed_id = lab.initial_id()
    sid = lab.add_device("2911", "R9")
    lab.link(seed_id, "GigabitEthernet0/0", sid, "GigabitEthernet0/0")
    links = lab.net.find("LINKS")
    assert links is not None
    assert any(L.find("CABLE").findtext("FROM") == seed_id for L in links.findall("LINK"))
    lab.prune_seed_devices()
    # no dangling link may reference a removed seed device (orphan links corrupt
    # the file); the seed's own inter-device links go with their devices
    for L in links.findall("LINK"):
        cab = L.find("CABLE")
        assert seed_id not in (cab.findtext("FROM"), cab.findtext("TO"))
        assert sid in (cab.findtext("FROM"), cab.findtext("TO"))


def test_prune_seed_devices_keeps_generated_links(lab):
    a = lab.add_device("2911", "R9")
    b = lab.add_device("2960-24TT", "SW9")
    lab.prune_seed_devices()
    lab.link(a, "GigabitEthernet0/0", b, "GigabitEthernet0/1")
    links = lab.net.find("LINKS")
    assert links is not None and len(links.findall("LINK")) == 1
    cab = links.find("LINK/CABLE")
    assert cab.findtext("FROM") == a and cab.findtext("TO") == b


# --------------------------------------------------------------------------- #
# automatic cable annotations
# --------------------------------------------------------------------------- #
def test_link_adds_workspace_note_with_interfaces_and_subnet(lab):
    lab.prune_seed_devices()
    r1 = lab.add_device(
        "2911", "R1",
        ios_config=["interface GigabitEthernet0/0",
                    " ip address 10.0.12.1 255.255.255.252",
                    " no shutdown", "end"],
    )
    r2 = lab.add_device(
        "2911", "R2",
        ios_config=["interface GigabitEthernet0/0",
                    " ip address 10.0.12.2 255.255.255.252",
                    " no shutdown", "end"],
    )

    lab.link(r1, "GigabitEthernet0/0", r2, "GigabitEthernet0/0")

    note = lab._pw.find("NOTES/NOTE")
    assert note is not None
    assert note.findtext("TEXT") == (
        "R1 GigabitEthernet0/0 <-> R2 GigabitEthernet0/0\n10.0.12.0/30"
    )
    assert note.findtext("NOTECLUSTERID") == "1-1"
    assert note.get("uuid", "").startswith("{")


def test_link_annotation_resolves_hwic_access_vlan_to_svi_subnet(lab):
    lab.prune_seed_devices()
    r1 = lab.add_device(
        "2911", "R1",
        ios_config=["interface FastEthernet0/1/0",
                    " switchport mode access",
                    " switchport access vlan 12",
                    "interface Vlan12",
                    " ip address 10.0.12.1 255.255.255.252",
                    " no shutdown", "end"],
    )
    r2 = lab.add_device(
        "2911", "R2",
        ios_config=["interface GigabitEthernet0/0",
                    " ip address 10.0.12.2 255.255.255.252",
                    " no shutdown", "end"],
    )

    lab.link(r1, "FastEthernet0/1/0", r2, "GigabitEthernet0/0")

    assert lab._pw.findtext("NOTES/NOTE/TEXT") == (
        "R1 FastEthernet0/1/0 <-> R2 GigabitEthernet0/0\n10.0.12.0/30"
    )


def test_link_annotation_can_override_subnet_and_position(lab):
    lab.prune_seed_devices()
    a = lab.add_device("2911", "R1")
    b = lab.add_device("2911", "R2")

    lab.link(a, "GigabitEthernet0/0", b, "GigabitEthernet0/0",
             subnet="198.51.100.0/30", label_position=(321, 456))

    note = lab._pw.find("NOTES/NOTE")
    assert note is not None
    assert note.findtext("TEXT").endswith("\n198.51.100.0/30")
    assert (note.findtext("X"), note.findtext("Y")) == ("321", "456")


def test_link_annotation_can_be_disabled_per_link_or_lab(lab):
    lab.prune_seed_devices()
    a = lab.add_device("2911", "R1")
    b = lab.add_device("2911", "R2")
    c = lab.add_device("2911", "R3")
    d = lab.add_device("2911", "R4")

    lab.link(a, "GigabitEthernet0/0", b, "GigabitEthernet0/0", annotate=False)
    lab.link(c, "GigabitEthernet0/0", d, "GigabitEthernet0/0")
    assert len(lab._pw.findall("NOTES/NOTE")) == 1

    models, modules = lab_api.load_templates(str(TOOLS / "device_templates.json"))
    quiet_lab = lab_api.Lab(
        str(TOOLS / "network_seed.xml"), models, modules, annotate_links=False
    )
    quiet_lab.prune_seed_devices()
    a = quiet_lab.add_device("2911", "R1")
    b = quiet_lab.add_device("2911", "R2")
    quiet_lab.link(a, "GigabitEthernet0/0", b, "GigabitEthernet0/0")
    assert not quiet_lab._pw.findall("NOTES/NOTE")


def test_pruning_seed_devices_removes_link_annotations(lab):
    seed_id = lab.initial_id()
    generated = lab.add_device("2911", "R9")
    lab.link(seed_id, "GigabitEthernet0/0", generated, "GigabitEthernet0/0")
    assert len(lab._pw.findall("NOTES/NOTE")) == 1

    lab.prune_seed_devices()

    assert lab._pw.find("NOTES/NOTE") is None
