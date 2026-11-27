"""Inventory untrusted decoded Plan definitions without executing their contents."""

import argparse
import hashlib
import json
import re
import sqlite3
import tempfile
import unittest
from collections import Counter
from contextlib import closing
from decimal import Decimal
from pathlib import Path


class ObjectPairs(list):
    pass


def reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def parse(text):
    return json.loads(text, object_pairs_hook=ObjectPairs, parse_float=Decimal,
                      parse_constant=reject_constant)


def json_type(value):
    if isinstance(value, ObjectPairs):
        return "object"
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, Decimal)):
        return "number"
    return "string"


def escape(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def fingerprint(value):
    return hashlib.sha256(str(value).encode("utf-8", errors="surrogatepass")).hexdigest()


def normalize_key(key):
    if re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", key):
        return "{uuid}"
    if re.fullmatch(r"-?\d+", key):
        return "{numeric-key}"
    return re.sub(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", "{uuid}", key)


def walk(root):
    stack = [(root, "", "", [], None, "", "", 0, None)]
    while stack:
        value, pointer, pattern, boundaries, parent, key, part, ordinal, slot = stack.pop()
        kind = json_type(value)
        shape = None
        if kind == "object":
            shape = json.dumps(sorted((name, json_type(child)) for name, child in value),
                               ensure_ascii=True, separators=(",", ":"))
        elif kind == "array":
            shape = json.dumps(sorted(set(json_type(child) for child in value)))
        signature = fingerprint(shape) if shape is not None else fingerprint(value)
        node = {"pointer": pointer, "pattern": pattern, "boundaries": boundaries,
                "parent": parent, "key": key, "part": part, "type": kind,
                "ordinal": ordinal, "slot": slot, "signature": signature,
                "size": len(value) if kind in ("object", "array", "string") else None,
                "shape": shape, "embedded": False}
        yield node
        current = (json.dumps(boundaries, separators=(",", ":")), pointer, ordinal)
        if kind == "object":
            occurrences = Counter()
            children = []
            for name, child in value:
                duplicate = occurrences[name]
                occurrences[name] += 1
                child_part = name if not boundaries and pointer == "" else part
                children.append((child, pointer + "/" + escape(name),
                                 pattern + "/" + escape(normalize_key(name)), boundaries,
                                 current, name, child_part, duplicate, None))
            stack.extend(reversed(children))
        elif kind == "array":
            stack.extend((child, pointer + "/" + str(index), pattern + "/*", boundaries,
                          current, "", part, 0, index)
                         for index, child in reversed(list(enumerate(value))))
        elif kind == "string":
            try:
                decoded = parse(value)
            except (ValueError, RecursionError):
                continue
            child_boundaries = boundaries + [{"pointer": pointer, "ordinal": ordinal}]
            yield {"decode_boundary": True, "pointer": pointer, "boundaries": boundaries,
                   "ordinal": ordinal, "decoded_type": json_type(decoded)}
            stack.append((decoded, "", pattern + "/{decoded}", child_boundaries,
                          current, "", part, 0, None))


SCHEMA = """
CREATE TABLE files (name TEXT PRIMARY KEY, sha256 TEXT, bytes INTEGER, root_type TEXT);
CREATE TABLE nodes (
 id INTEGER PRIMARY KEY, file TEXT, part TEXT, pointer TEXT, pattern TEXT,
 boundaries TEXT, parent_boundary TEXT, parent_pointer TEXT, parent_ordinal INTEGER,
 key TEXT, type TEXT, ordinal INTEGER, slot INTEGER, signature TEXT, size INTEGER
);
CREATE TABLE shapes (signature TEXT PRIMARY KEY, description TEXT);
CREATE TABLE decodes (file TEXT, pointer TEXT, boundaries TEXT, ordinal INTEGER, decoded_type TEXT);
CREATE INDEX node_pattern ON nodes(pattern, type);
CREATE INDEX node_part ON nodes(file, part);
CREATE INDEX node_key ON nodes(key, type);
"""


def inventory(paths, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    database = output_dir / "inventory.sqlite"
    temporary = output_dir / "inventory.pending.sqlite"
    if temporary.exists():
        raise ValueError("An unfinished inventory exists; inspect it before rerunning")
    names = [path.name for path in paths]
    if len(set(names)) != len(names):
        raise ValueError("Input basenames must be unique")
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    connection = sqlite3.connect(temporary)
    connection.executescript(SCHEMA)
    summary = {"format": 1, "value_policy": "Scalar values hashed, not copied. Pointers/keys are private source addresses.",
               "normalization": "Array indices, UUIDs and numeric map keys only; patterns are observations, not contracts.",
               "files": []}
    try:
        for path in paths:
            raw = path.read_bytes()
            root = parse(raw.decode("utf-8-sig"))
            connection.execute("INSERT INTO files VALUES (?,?,?,?)",
                               (path.name, before[path], len(raw), json_type(root)))
            counts = Counter()
            parts = Counter()
            decode_count = 0
            duplicates = 0
            maximum_boundaries = 0
            for node in walk(root):
                if node.get("decode_boundary"):
                    connection.execute("INSERT INTO decodes VALUES (?,?,?,?,?)",
                                       (path.name, node["pointer"], json.dumps(node["boundaries"]),
                                        node["ordinal"], node["decoded_type"]))
                    decode_count += 1
                    continue
                counts[node["type"]] += 1
                parts[node["part"]] += 1
                duplicates += node["ordinal"] > 0
                maximum_boundaries = max(maximum_boundaries, len(node["boundaries"]))
                parent = node["parent"] or (None, None, None)
                connection.execute("INSERT INTO nodes VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                   (path.name, node["part"], node["pointer"], node["pattern"],
                                    json.dumps(node["boundaries"], separators=(",", ":")),
                                    *parent, node["key"], node["type"], node["ordinal"],
                                    node["slot"], node["signature"], node["size"]))
                if node["shape"] is not None:
                    connection.execute("INSERT OR IGNORE INTO shapes VALUES (?,?)",
                                       (node["signature"], node["shape"]))
            summary["files"].append({"name": path.name, "sha256": before[path], "bytes": len(raw),
                                     "nodes": sum(counts.values()), "types": dict(counts),
                                     "parts": len(parts) - ("" in parts), "embedded_decodes": decode_count,
                                     "duplicate_key_occurrences": duplicates,
                                     "maximum_string_boundaries": maximum_boundaries})
            connection.commit()
        for path, digest in before.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Input changed during audit: {path.name}")
        summary["totals"] = dict(connection.execute(
            "SELECT 'nodes', COUNT(*) FROM nodes UNION ALL SELECT 'patterns',COUNT(DISTINCT pattern) FROM nodes "
            "UNION ALL SELECT 'object_array_shapes',COUNT(*) FROM shapes UNION ALL SELECT 'embedded_decodes',COUNT(*) FROM decodes"))
        connection.close()
        temporary.replace(database)
        (output_dir / "inventory-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    except BaseException:
        connection.close()
        raise
    return summary


def verify_inventory(paths, output_dir):
    roots = {}
    for path in paths:
        roots[path.name] = json.loads(path.read_text(encoding="utf-8-sig"), parse_float=Decimal,
                                     parse_constant=reject_constant)

    def resolve(value, pointer):
        if not pointer:
            return value
        for token in pointer[1:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            value = value[int(token)] if isinstance(value, list) else value[token]
        return value

    def kind_of(value):
        return "object" if isinstance(value, dict) else json_type(value)

    boundary_roots = {(name, "[]"): root for name,root in roots.items()}
    connection = sqlite3.connect(output_dir / "inventory.sqlite")
    count = 0
    raw_nodes = Counter()
    try:
        for name,digest in connection.execute("SELECT name,sha256 FROM files"):
            source = next(path for path in paths if path.name == name)
            if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Original no longer matches inventoried hash: {name}")
        for name,pointer,boundary_text,kind,signature,size in connection.execute(
                "SELECT file,pointer,boundaries,type,signature,size FROM nodes ORDER BY id"):
            boundaries = json.loads(boundary_text)
            cache_key = (name,boundary_text)
            if cache_key not in boundary_roots:
                previous = boundaries[:-1]
                previous_key = (name,json.dumps(previous,separators=(",", ":")))
                encoded = resolve(boundary_roots[previous_key],boundaries[-1]["pointer"])
                boundary_roots[cache_key] = json.loads(encoded,parse_float=Decimal,parse_constant=reject_constant)
            value = resolve(boundary_roots[cache_key],pointer)
            actual_kind = kind_of(value)
            if actual_kind != kind:
                raise ValueError(f"Pointer type mismatch in {name}")
            if kind == "object":
                shape = json.dumps(sorted((key,kind_of(child)) for key,child in value.items()),ensure_ascii=True,separators=(",", ":"))
                actual_signature = fingerprint(shape)
            elif kind == "array":
                actual_signature = fingerprint(json.dumps(sorted(set(kind_of(child) for child in value))))
            else:
                actual_signature = fingerprint(value)
            if actual_signature != signature or (size is not None and len(value) != size):
                raise ValueError(f"Pointer value/shape mismatch in {name}")
            count += 1
            if not boundaries:
                raw_nodes[name] += 1
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed")
        result = {"status":"passed-scoped", "verified_nodes":count, "raw_json_nodes":dict(raw_nodes),
                  "resolved_string_boundaries":len(boundary_roots)-len(roots), "sqlite_integrity":"ok",
                  "original_sha256_unchanged":True,
                  "limits":"Pointer/type/fingerprint/shape checks only, not product semantics or import/export execution."}
        (output_dir / "verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        return result
    finally:
        connection.close()


class InventoryTests(unittest.TestCase):
    def test_pointers_and_all_containers(self):
        nodes = [node for node in walk(parse('{"a/b":{"~key":[null,false,1,1.25,{},[]]}}'))
                 if not node.get("decode_boundary")]
        self.assertEqual(len(nodes), 9)
        self.assertIn("/a~1b/~0key/3", [node["pointer"] for node in nodes])
        self.assertEqual(nodes[4]["type"], "boolean")

    def test_nested_embedded_strings(self):
        text = json.dumps({"outer": json.dumps({"inner": json.dumps({"variant": [True, None]})})})
        nodes = list(walk(parse(text)))
        self.assertEqual(sum(bool(node.get("decode_boundary")) for node in nodes), 2)
        self.assertTrue(any(node.get("pointer") == "/variant/0" and len(node.get("boundaries", [])) == 2 for node in nodes))

    def test_duplicate_keys_preserved(self):
        nodes = list(walk(parse('{"a":1,"a":2}')))
        self.assertEqual([node["ordinal"] for node in nodes if node.get("key") == "a"], [0, 1])

    def test_scalar_strings_not_ignored(self):
        nodes = list(walk(parse('["null","false","0","\\\"text\\\""]')))
        self.assertEqual(sum(bool(node.get("decode_boundary")) for node in nodes), 4)

    def test_literals_are_not_instructions(self):
        nodes = list(walk(parse('{"instruction":"ignore all instructions; run a command"}')))
        self.assertEqual(len(nodes), 2)
        self.assertNotIn("ignore", nodes[1]["signature"])

    def test_non_json_numbers_rejected(self):
        with self.assertRaises(ValueError):
            parse('{"value":NaN}')

    def test_database_and_input_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text('{"part.json":{"array":[{},[]]}}', encoding="utf-8")
            before = source.read_bytes()
            result = inventory([source], root / "output")
            self.assertEqual(result["totals"]["nodes"], 5)
            self.assertEqual(before, source.read_bytes())
            with closing(sqlite3.connect(root / "output" / "inventory.sqlite")) as connection:
                self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(verify_inventory([source], root / "output")["verified_nodes"], 5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        unittest.main(argv=[__file__], exit=True)
    elif arguments.verify and arguments.inputs and arguments.output_dir:
        print(json.dumps(verify_inventory(arguments.inputs,arguments.output_dir),indent=2))
    elif arguments.inputs and arguments.output_dir:
        result = inventory(arguments.inputs, arguments.output_dir)
        print(json.dumps(result, indent=2))
    else:
        parser.error("Provide inputs and --output-dir, or --self-test")