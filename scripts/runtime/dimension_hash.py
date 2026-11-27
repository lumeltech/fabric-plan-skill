"""Native seed-zero XXH3-64 dimension identity and ordered-pivot hash.

Matches the supplied hash-wasm snippet. Uses the bundled XXH3 implementation;
no JavaScript runtime, npm package, saved donor hash or network is needed.
"""
from .identity import native_id, xxh3


def generate_dimension_id(source_id):
    """Hash the exact original metadata field ID once, preserving UTF-8 bytes."""
    if not isinstance(source_id, str):
        raise TypeError('source_id must be a string')
    return str(xxh3(source_id))


def generate_dimension_hash(row_ids, col_ids):
    """Hash ALL current ordered pivot dimensions, not the anchor subset.

    IDs are canonical unsigned 64-bit decimal strings. [] is a valid empty
    axis. Native Rust {:x} formatting is lowercase hex without leading zeros.
    """
    for ids in (row_ids, col_ids):
        if not isinstance(ids, list):
            raise TypeError('Dimension IDs must be lists of canonical u64 decimal strings')
        for value in ids:
            native_id(value)
    return format(xxh3('-'.join(row_ids) + '__' + '-'.join(col_ids)), 'x')
