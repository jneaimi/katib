"""Phase-4 — content hash determinism + sensitivity.

The content_hash is the integrity anchor for `.katib-pack` files. We
need two things from it: (1) determinism — the same set of files
hashes to the same value every time, on any machine, regardless of
when the pack was built; (2) sensitivity — any change to the file
contents produces a different hash.

The deterministic-tar work in `core.pack.build_canonical_tar_body`
is what makes (1) possible. (2) is just a sanity check on SHA-256.
"""
from __future__ import annotations

from core import pack


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_same_inputs_produce_same_hash():
    files = [("a/foo.txt", b"hello"), ("a/bar.txt", b"world")]
    body1 = pack.build_canonical_tar_body(files)
    body2 = pack.build_canonical_tar_body(files)
    assert pack.compute_content_hash(body1) == pack.compute_content_hash(body2)


def test_input_order_does_not_affect_hash():
    """Files are sorted alphabetically before being added to the tar,
    so the caller's order of arguments must not affect the hash."""
    a = [("a/foo.txt", b"hello"), ("a/bar.txt", b"world")]
    b = [("a/bar.txt", b"world"), ("a/foo.txt", b"hello")]
    h_a = pack.compute_content_hash(pack.build_canonical_tar_body(a))
    h_b = pack.compute_content_hash(pack.build_canonical_tar_body(b))
    assert h_a == h_b


def test_hash_format_is_sha256_prefixed_hex():
    body = pack.build_canonical_tar_body([("foo.txt", b"x")])
    h = pack.compute_content_hash(body)
    assert h.startswith("sha256:")
    digest = h[len("sha256:"):]
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


# ---------------------------------------------------------------------------
# Sensitivity — any byte change flips the hash
# ---------------------------------------------------------------------------


def test_changing_a_file_byte_changes_hash():
    a = [("foo.txt", b"hello")]
    b = [("foo.txt", b"hellp")]   # one byte different
    h_a = pack.compute_content_hash(pack.build_canonical_tar_body(a))
    h_b = pack.compute_content_hash(pack.build_canonical_tar_body(b))
    assert h_a != h_b


def test_renaming_a_file_changes_hash():
    a = [("foo.txt", b"hello")]
    b = [("bar.txt", b"hello")]
    h_a = pack.compute_content_hash(pack.build_canonical_tar_body(a))
    h_b = pack.compute_content_hash(pack.build_canonical_tar_body(b))
    assert h_a != h_b


def test_adding_a_file_changes_hash():
    a = [("foo.txt", b"hello")]
    b = [("foo.txt", b"hello"), ("bar.txt", b"world")]
    h_a = pack.compute_content_hash(pack.build_canonical_tar_body(a))
    h_b = pack.compute_content_hash(pack.build_canonical_tar_body(b))
    assert h_a != h_b


def test_empty_input_produces_stable_empty_hash():
    """An empty pack still hashes deterministically."""
    h1 = pack.compute_content_hash(pack.build_canonical_tar_body([]))
    h2 = pack.compute_content_hash(pack.build_canonical_tar_body([]))
    assert h1 == h2
    assert h1.startswith("sha256:")


# ---------------------------------------------------------------------------
# Tar mtime / uid / gid normalization (the determinism mechanism)
# ---------------------------------------------------------------------------


def test_tar_body_has_zero_mtime_for_all_entries():
    """If any entry kept the wall-clock mtime, the hash would change
    every time the pack is built. Verify normalization holds."""
    import io
    import tarfile

    body = pack.build_canonical_tar_body([("a.txt", b"x"), ("b.txt", b"y")])
    with tarfile.open(fileobj=io.BytesIO(body), mode="r") as tar:
        for info in tar.getmembers():
            assert info.mtime == 0, f"{info.name} has non-zero mtime {info.mtime}"
            assert info.uid == 0
            assert info.gid == 0
            assert info.uname == ""
            assert info.gname == ""


def test_tar_body_entries_are_sorted():
    """Entries must be sorted alphabetically inside the tarball,
    independent of input order."""
    import io
    import tarfile

    files = [
        ("zeta/file.txt", b"z"),
        ("alpha/file.txt", b"a"),
        ("middle/file.txt", b"m"),
    ]
    body = pack.build_canonical_tar_body(files)
    with tarfile.open(fileobj=io.BytesIO(body), mode="r") as tar:
        names = [info.name for info in tar.getmembers()]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# PACK_FORMAT_VERSION exposed
# ---------------------------------------------------------------------------


def test_pack_format_version_is_one():
    """Frozen at 1 for v1.0.0. Future bumps require a new ADR."""
    assert pack.PACK_FORMAT_VERSION == 1
