# Plan a transformation and resolve its output

Use a direct model binding when the source already supplies the requested
value at the correct grain. Use a sheet binding for an existing sheet output
at compatible grain. Only plan a transformation when the requested result
needs a join, union, aggregation or other explicit change in grain.

For an append, align names, types and units across inputs. For a merge or join,
declare the join type and key on each side; check uniqueness on the lookup side
or identify the intended multiplicity. A measure at company × month cannot be
assigned to each customer as a customer amount without an allocation rule.

```sh
python plan.py construct-bridge join --input join-request.json --out query.json
python plan.py check-bridge-mappings --input graph.json --out checks.json
```

These commands operate on supplied metadata, not on rows in a workspace.
Keep query identity separate from source identity and resolve each
post-transform output by its current ID/type. Renaming a label or selecting
an input ordinal does not establish which output a consumer reads. Preserve
consumer identity when correcting a binding. A constructed graph does not
prove refresh, materialization, row counts or financial correctness.
