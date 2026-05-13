# Nova Impact Accounting Standard

On the [Nova Impact Accounting Standard](https://nova.org.za/novaimpactaccountingstandard), a standard provides the following artefacts:

* A **glossary** in the form of a `skos:ConceptScheme` with its terms, definitions and taxonomies.
* A list of relevant **indicators** (expressed in terms of the Indicator Ontology), as a `skos:ConceptScheme`
* A list of relevant **methodologies** (expressed in terms of the Methodology Ontology), as a `skos:ConceptScheme`
* The **data requirements** for all actions (defined in the glossary) that can be performed in terms of the standard, as SHACL constraints. Think of this as a set of templates. If it is required that actions be performed in a specific sequence, this is enforced by making a reference to the resulting artefact of a preceding step a requirement in a subsequent step. These can be tested and compiled to UIs of various formats and for various platforms using [shape2flutter](https://github.com/IndependentImpact/shape2flutter). 
* The **reputation requirement** for all actions that can be performed in terms of the standard, as SHACL constraints. The reputation requirements refer to either an existing `skos:ConceptScheme` with skills and knowledge domains, or one must accompany the standard. 
