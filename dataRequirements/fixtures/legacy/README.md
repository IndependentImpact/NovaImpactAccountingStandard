# Legacy RDF Fixtures

These fixtures are minimal Turtle representations of the RDF graphs emitted by
the frozen `reference/` adapters.

They intentionally preserve legacy behavior, including older namespace IRIs and
plain literal date-time values. Phase 1 is responsible for normalizing these
graphs to canonical namespaces, typed values, stable concept IRIs, and final
SHACL-compatible structures.

Use these files as small regression examples for adapter branches before and
during SHACL migration. They are not the final canonical data examples.
