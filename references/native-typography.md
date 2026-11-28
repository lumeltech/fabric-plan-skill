# Native chart typography completion

Arial on all authored text is this package's convention rather than a Fabric
requirement, and it has no declination switch: the builder authors it into the
definition, and `check-application-defaults` rejects non-Arial fonts, including
effective Matrix overrides and service-expanded `hiddenProperties_!!!_*` JSON.

To normalize existing fonts in a candidate, apply
`runtime.application_typography.normalize_arial(properties)` to each affected
visual's properties in a fresh export. It covers the documented serialized style
boundaries (appearance, axes and secondary visual styles), existing font keys,
rich-text CSS and matrix font overrides without interpreting arbitrary strings.
Unknown formulas, field assignments and data remain unchanged, and embedded inputs
are never cloned. Publish the candidate with `api update`, then export again and
compare. Reading saved fonts back from a native expansion has no public route.
This checks saved definition styling, not UI rendering.

For an unrelated existing-report repair, retain intentional typography. Normalize
only for new application defaults or an expressly requested font change.
