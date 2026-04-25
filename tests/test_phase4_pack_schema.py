"""Phase-4 — pack.yaml schema validates the share-format manifest.

The schema is the public contract for `.katib-pack` files at v1.0.0.
We test it by feeding canonical-good and pathological-bad manifests
through `validate_manifest_dict()` and asserting the right pass/fail
outcomes.
"""
from __future__ import annotations

import copy

import pytest

from core import pack


VALID_MANIFEST = {
    "pack_format": 1,
    "name": "jneaimi/client-proposal",
    "version": "1.2.0",
    "content_hash": "sha256:" + "a" * 64,
    "contents": {
        "components": [
            {"name": "client-hero", "tier": "section", "version": "0.1.0"},
            {"name": "client-stat", "tier": "primitive"},
        ],
        "recipes": [
            {"name": "client-proposal", "version": "1.2.0"},
        ],
        "brands": [
            {"name": "acme"},
        ],
    },
    "requires": {
        "katib_min": "1.0.0",
        "bundled_components": ["module", "kv-list"],
    },
    "author": {
        "name": "Jasem Al Neaimi",
        "email": "jneaimi@gmail.com",
        "url": "https://jneaimi.com",
    },
    "license": "MIT",
    "description": "Client proposal recipe with bespoke hero + stat block.",
    "tags": ["proposal", "business", "bilingual"],
    "domain": "business",
}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_manifest_passes():
    assert pack.validate_manifest_dict(VALID_MANIFEST) == []


def test_minimal_manifest_passes():
    """Only required fields should be enough."""
    minimal = {
        "pack_format": 1,
        "name": "jneaimi/client-proposal",
        "version": "1.0.0",
        "content_hash": "sha256:" + "0" * 64,
        "contents": {},
        "requires": {},
    }
    assert pack.validate_manifest_dict(minimal) == []


# ---------------------------------------------------------------------------
# Required fields
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing_key", [
    "pack_format", "name", "version", "content_hash", "contents", "requires",
])
def test_missing_required_field_rejected(missing_key):
    bad = copy.deepcopy(VALID_MANIFEST)
    del bad[missing_key]
    errors = pack.validate_manifest_dict(bad)
    assert errors, f"expected error for missing {missing_key}"


# ---------------------------------------------------------------------------
# Pack format version
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_version", [0, 2, 99, -1, "1", "1.0"])
def test_bad_pack_format_rejected(bad_version):
    bad = copy.deepcopy(VALID_MANIFEST)
    bad["pack_format"] = bad_version
    errors = pack.validate_manifest_dict(bad)
    assert errors, f"expected error for pack_format={bad_version!r}"


# ---------------------------------------------------------------------------
# Pack name shape
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_name", [
    "client-proposal",            # missing slash
    "Jneaimi/client-proposal",    # uppercase author
    "jneaimi/Client-Proposal",    # uppercase artifact
    "jneaimi/client_proposal",    # underscore
    "jneaimi//double-slash",      # empty middle
    "/leading-slash",             # empty author
    "trailing-slash/",            # empty artifact
    "jneaimi/client/proposal",    # multiple slashes
    "1jneaimi/client",            # leading digit
    "",                           # empty
])
def test_bad_pack_name_rejected(bad_name):
    bad = copy.deepcopy(VALID_MANIFEST)
    bad["name"] = bad_name
    errors = pack.validate_manifest_dict(bad)
    assert errors, f"expected error for name={bad_name!r}"


@pytest.mark.parametrize("good_name", [
    "jneaimi/client-proposal",
    "j/c",
    "abc-co/some-pack",
    "vendor1/pack-v2",
])
def test_good_pack_names_accepted(good_name):
    good = copy.deepcopy(VALID_MANIFEST)
    good["name"] = good_name
    assert pack.validate_manifest_dict(good) == [], f"name={good_name!r} should be valid"


# ---------------------------------------------------------------------------
# Version + content_hash
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_version", [
    "1", "1.0", "v1.0.0", "1.0.0.0", "alpha", "",
])
def test_bad_version_rejected(bad_version):
    bad = copy.deepcopy(VALID_MANIFEST)
    bad["version"] = bad_version
    errors = pack.validate_manifest_dict(bad)
    assert errors


@pytest.mark.parametrize("bad_hash", [
    "abc",                        # too short
    "sha256:abc",                 # too short hex
    "sha512:" + "a" * 64,         # wrong algorithm
    "sha256:" + "a" * 63,         # one short
    "sha256:" + "a" * 65,         # one long
    "sha256:" + "g" * 64,         # bad hex char
    "SHA256:" + "a" * 64,         # uppercase prefix
    "a" * 64,                     # missing prefix
])
def test_bad_content_hash_rejected(bad_hash):
    bad = copy.deepcopy(VALID_MANIFEST)
    bad["content_hash"] = bad_hash
    errors = pack.validate_manifest_dict(bad)
    assert errors, f"expected error for content_hash={bad_hash!r}"


# ---------------------------------------------------------------------------
# Extra top-level keys
# ---------------------------------------------------------------------------


def test_extra_top_level_key_rejected():
    bad = copy.deepcopy(VALID_MANIFEST)
    bad["future_field"] = "whatever"
    errors = pack.validate_manifest_dict(bad)
    assert errors


# ---------------------------------------------------------------------------
# Reserved Phase-7 fields are accepted but optional
# ---------------------------------------------------------------------------


def test_signature_field_accepted():
    """The schema reserves `signature` and `signed_by` for Phase 7;
    they should not be rejected by Phase-4 validation."""
    good = copy.deepcopy(VALID_MANIFEST)
    good["signature"] = "ed25519:xxx"
    good["signed_by"] = "jneaimi"
    assert pack.validate_manifest_dict(good) == []


# ---------------------------------------------------------------------------
# load_manifest + dump_manifest round-trip
# ---------------------------------------------------------------------------


def test_dump_and_load_round_trip(tmp_path):
    m = pack.PackManifest(
        pack_format=1,
        name="jneaimi/test-pack",
        version="0.1.0",
        content_hash="sha256:" + "f" * 64,
        contents={"recipes": [{"name": "foo"}]},
        requires={"katib_min": "1.0.0"},
        author={"name": "Test User"},
        license="MIT",
        description="Test pack",
        tags=["test"],
    )
    path = tmp_path / "pack.yaml"
    path.write_text(pack.dump_manifest(m), encoding="utf-8")
    loaded = pack.load_manifest(path)
    assert loaded.name == m.name
    assert loaded.version == m.version
    assert loaded.content_hash == m.content_hash
    assert loaded.contents == m.contents
    assert loaded.requires == m.requires
    assert loaded.author == m.author
    assert loaded.license == m.license
    assert loaded.tags == m.tags


def test_load_manifest_rejects_bad_yaml(tmp_path):
    path = tmp_path / "pack.yaml"
    path.write_text("pack_format: 99\nname: invalid\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid pack manifest"):
        pack.load_manifest(path)


# ---------------------------------------------------------------------------
# parse_pack_name
# ---------------------------------------------------------------------------


def test_parse_pack_name_splits_on_slash():
    author, artifact = pack.parse_pack_name("jneaimi/client-proposal")
    assert author == "jneaimi"
    assert artifact == "client-proposal"


def test_parse_pack_name_rejects_no_slash():
    with pytest.raises(ValueError, match="missing slash"):
        pack.parse_pack_name("client-proposal")
