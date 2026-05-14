# Phase 4 compatibility adapters.
# Source this file instead of the frozen legacy scripts in reference/.

nias_context <- function() {
  list(
    "aiao" = "http://w3id.org/aiao#",
    "claimont" = "http://w3id.org/claimont#",
    "data" = "https://jellyfiiish.xyz/ns/",
    "dcterms" = "http://purl.org/dc/terms/",
    "ghg-m" = "https://nova.org.za/novaimpactaccountingstandard/methodologies/ghg/",
    "hedera" = "https://hashgraphontology.xyz/core/",
    "impactont" = "http://w3id.org/impactont#",
    "ind" = "http://independentimpact.org/indicator-owl/",
    "infocomm" = "http://w3id.org/infocomm#",
    "meth" = "http://independentimpact.org/methodology/",
    "nias-cs" = "https://nova.org.za/novaimpactaccountingstandard/",
    "nias-ind" = "https://nova.org.za/novaimpactaccountingstandard/indicators/",
    "nias-o" = "https://nova.org.za/novaimpactaccountingstandard/",
    "rdf" = "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs" = "http://www.w3.org/2000/01/rdf-schema#",
    "schema" = "https://schema.org/",
    "skos" = "http://www.w3.org/2004/02/skos/core#",
    "time" = "http://www.w3.org/2006/time#",
    "unit" = "http://qudt.org/vocab/unit/",
    "xsd" = "http://www.w3.org/2001/XMLSchema#"
  )
}

nias_get <- function(x, name, default = NULL) {
  if (is.null(x) || length(x) == 0) {
    return(default)
  }
  if (is.data.frame(x)) {
    if (name %in% names(x) && nrow(x) > 0) {
      return(x[[name]][1])
    }
    return(default)
  }
  if (is.list(x) && name %in% names(x)) {
    return(x[[name]])
  }
  default
}

nias_has_value <- function(x) {
  if (missing(x) || is.null(x) || length(x) == 0) {
    return(FALSE)
  }
  if (is.atomic(x) && length(x) == 1) {
    if (is.na(x)) {
      return(FALSE)
    }
    if (trimws(as.character(x)) == "") {
      return(FALSE)
    }
  }
  TRUE
}

nias_add_if_present <- function(res, name, value) {
  if (nias_has_value(value)) {
    res[[name]] <- value
  }
  res
}

nias_enum <- function(x) {
  toupper(gsub("[^A-Za-z0-9]+", "_", trimws(as.character(x))))
}

nias_slug <- function(x, fallback = "unknown") {
  if (!nias_has_value(x)) {
    return(fallback)
  }
  slug <- tolower(trimws(as.character(x)))
  slug <- gsub("&", "and", slug, fixed = TRUE)
  slug <- gsub("[^a-z0-9]+", "-", slug)
  slug <- gsub("(^-+|-+$)", "", slug)
  if (slug == "") fallback else slug
}

nias_iri <- function(id, prefix, slug_prefix = NULL) {
  if (!nias_has_value(id)) {
    return(NULL)
  }
  value <- as.character(id)
  if (grepl("^[A-Za-z][A-Za-z0-9+.-]*:", value)) {
    return(value)
  }
  paste0(prefix, if (is.null(slug_prefix)) value else paste0(slug_prefix, value))
}

nias_ref <- function(id) {
  list("@id" = id)
}

nias_lang <- function(value, language = "en") {
  list("@value" = as.character(value), "@language" = language)
}

nias_typed_literal <- function(value, datatype) {
  list("@value" = as.character(value), "@type" = datatype)
}

nias_datetime_literal <- function(value) {
  nias_typed_literal(value, "xsd:dateTimeStamp")
}

nias_any_uri_literal <- function(value) {
  nias_typed_literal(value, "xsd:anyURI")
}

nias_numeric <- function(value) {
  if (!nias_has_value(value)) {
    return(NULL)
  }
  numeric_value <- suppressWarnings(as.numeric(value))
  if (!is.na(numeric_value)) {
    return(numeric_value)
  }
  value
}

nias_bool <- function(value) {
  if (is.logical(value)) {
    return(value[1])
  }
  nias_enum(value) %in% c("YES", "TRUE", "1", "Y")
}

nias_map_concept <- function(value, mapping, field_name) {
  key <- nias_enum(value)
  if (key %in% names(mapping)) {
    return(mapping[[key]])
  }
  stop(sprintf("Unknown %s value: %s", field_name, as.character(value)))
}

nias_yes_no_concept <- function(value) {
  nias_map_concept(value, c(YES = "nias-cs:yes", NO = "nias-cs:no"), "yes/no")
}

nias_project_iri <- function(project_id) {
  nias_iri(project_id, "nias-o:", "activities/")
}

nias_agent_iri <- function(agent_id) {
  nias_iri(agent_id, "nias-o:", "agents/")
}

nias_document_iri <- function(document_id) {
  nias_iri(document_id, "nias-o:", "documents/")
}

nias_unit_iri <- function(uom) {
  if (!nias_has_value(uom)) {
    warning("Missing unit of measure; falling back to unit:UNITLESS.")
    return("unit:UNITLESS")
  }
  key <- toupper(gsub("[^A-Za-z0-9]+", "", as.character(uom)))
  unit_map <- c(
    TCO2E = "unit:TONNE",
    TCO2EYEAR = "unit:TONNE",
    TCO2EPERYEAR = "unit:TONNE",
    TONNE = "unit:TONNE",
    TONNES = "unit:TONNE",
    T = "unit:TONNE",
    KG = "unit:KiloGM",
    KILOGRAM = "unit:KiloGM",
    KWH = "unit:KiloW-HR",
    MWH = "unit:MegaW-HR",
    GWH = "unit:GigaW-HR",
    PERCENT = "unit:PERCENT",
    UNITLESS = "unit:UNITLESS"
  )
  if (key %in% names(unit_map)) {
    return(unit_map[[key]])
  }
  warning(sprintf("No QUDT unit mapping for '%s'; minting a draft NIAS unit IRI.", as.character(uom)))
  paste0("nias-o:units/draft/", nias_slug(uom))
}

nias_indicator_iri <- function(label = NULL, uom = NULL, indicator_id = NULL) {
  if (nias_has_value(indicator_id)) {
    return(nias_iri(indicator_id, "nias-ind:", ""))
  }
  label_key <- toupper(as.character(if (nias_has_value(label)) label else ""))
  uom_key <- toupper(as.character(if (nias_has_value(uom)) uom else ""))
  if (grepl("CO2|CO₂|TCO2|TCO₂|GHG", paste(label_key, uom_key))) {
    return("nias-ind:ghg-tco2e-per-year")
  }
  paste0("nias-ind:draft-", nias_slug(paste(label, uom)))
}

nias_methodology_iri <- function(label = NULL, title = NULL, methodology_id = NULL) {
  if (nias_has_value(methodology_id)) {
    return(nias_iri(methodology_id, "ghg-m:", ""))
  }
  raw_code <- if (nias_has_value(label)) as.character(label) else as.character(title)
  raw_code <- strsplit(raw_code, "\\s+")[[1]][1]
  raw_code <- gsub("\\.", "", raw_code)
  raw_code <- gsub("[^A-Za-z0-9]+", "-", raw_code)
  paste0("ghg-m:", nias_slug(raw_code))
}

nias_rows <- function(x) {
  if (!nias_has_value(x)) {
    return(list())
  }
  if (is.data.frame(x)) {
    return(lapply(seq_len(nrow(x)), function(i) as.list(x[i, , drop = FALSE])))
  }
  if (is.list(x) && is.null(names(x))) {
    return(x)
  }
  if (is.atomic(x)) {
    return(as.list(x))
  }
  list(x)
}

dateTimeInstant_toFluree <- function(x) {
  list(
    "@context" = nias_context(),
    "@type" = "time:Instant",
    "time:inXSDDateTimeStamp" = nias_datetime_literal(x)
  )
}

dateTimePeriod_toFluree <- function(start, end) {
  list(
    "@context" = nias_context(),
    "@type" = "time:Interval",
    "time:hasBeginning" = dateTimeInstant_toFluree(start),
    "time:hasEnd" = dateTimeInstant_toFluree(end)
  )
}

creditingPeriod_toFluree <- function(start, end, renewable) {
  res <- dateTimePeriod_toFluree(start, end)
  res[["@type"]] <- c("nias-o:CreditingPeriod", "time:Interval")
  res[["nias-o:creditingPeriodIsRenewable"]] <- as.logical(renewable)
  res
}

indicator_toFluree <- function(lbl, uom, indicatorId = NULL, description = NULL) {
  indicator_id <- nias_indicator_iri(label = lbl, uom = uom, indicator_id = indicatorId)
  res <- list(
    "@context" = nias_context(),
    "@id" = indicator_id,
    "@type" = c("ind:IndicatorDefinition", "skos:Concept"),
    "skos:prefLabel" = nias_lang(if (nias_has_value(lbl)) lbl else indicator_id),
    "ind:hasUnit" = nias_ref(nias_unit_iri(uom)),
    "ind:hasIndicatorStage" = nias_ref("ind:ImpactIndicator")
  )
  res <- nias_add_if_present(res, "dcterms:description", description)
  res
}

state_toFluree <- function(
    dtStart,
    dtEnd = NULL,
    mod,
    indic = NULL,
    indicId = NULL,
    val = NULL) {
  res <- list(
    "@context" = nias_context(),
    "@type" = "impactont:State",
    "impactont:hasTemporalLocation" = if (nias_has_value(dtEnd)) {
      dateTimePeriod_toFluree(start = dtStart, end = dtEnd)
    } else {
      dateTimeInstant_toFluree(dtStart)
    },
    "impactont:hasModality" = tolower(as.character(mod)),
    "impactont:isDefinedByIndicator" = if (nias_has_value(indicId)) {
      nias_ref(indicId)
    } else {
      indic
    }
  )
  if (nias_has_value(val)) {
    res[["impactont:hasIndicatorValue"]] <- list(
      "@type" = "impactont:IndicatorValue",
      "rdf:value" = nias_numeric(val)
    )
  }
  res
}

sMethodology_1x0x0_toFluree <- function(title = NULL, label = NULL, versionTag = NULL, methodologyId = NULL) {
  res <- list(
    "@context" = nias_context(),
    "@id" = nias_methodology_iri(label = label, title = title, methodology_id = methodologyId),
    "@type" = c("meth:Methodology", "skos:Concept")
  )
  res <- nias_add_if_present(res, "dcterms:title", if (nias_has_value(title)) nias_lang(title) else NULL)
  res <- nias_add_if_present(res, "skos:prefLabel", if (nias_has_value(label)) nias_lang(label) else NULL)
  res <- nias_add_if_present(res, "meth:methodCode", if (nias_has_value(label)) as.character(label) else NULL)
  res <- nias_add_if_present(res, "meth:hasVersion", if (nias_has_value(versionTag)) as.character(versionTag) else NULL)
  res
}

sTechnologyOrMeasure_1x0x0_toFluree <- function(lsData) {
  res <- list(
    "@context" = nias_context(),
    "@type" = "nias-o:TechnologyOrMeasure",
    "nias-o:techMeasType" = nias_ref(nias_map_concept(
      nias_get(lsData, "type_techmeas"),
      c(FACILITY = "nias-cs:facility", SYSTEM = "nias-cs:system", EQUIPMENT = "nias-cs:equipment", OTHER = "nias-cs:other"),
      "technology or measure type"
    )),
    "schema:description" = nias_get(lsData, "description")
  )
  res <- nias_add_if_present(res, "nias-o:currentAgeInYears", nias_numeric(nias_get(lsData, "age_current")))
  res <- nias_add_if_present(res, "nias-o:estimatedLifespanInYears", nias_numeric(nias_get(lsData, "lifespan_estimated")))
  additional_info <- nias_get(lsData, "info_additional")
  if (!nias_has_value(additional_info)) {
    additional_info <- nias_get(lsData, "type_techmeas_otherexplain")
  }
  res <- nias_add_if_present(res, "nias-o:additionalInfo", additional_info)
  res
}

projectParty_toFluree <- function(lsData) {
  res <- list(
    "@context" = nias_context(),
    "@type" = "nias-o:ProjectParty",
    "nias-o:partyName" = nias_get(lsData, "name"),
    "nias-o:isHostParty" = nias_bool(nias_get(lsData, "is_host")),
    "nias-o:isParticipantParty" = nias_bool(nias_get(lsData, "is_participant")),
    "nias-o:publicPrivateClassification" = nias_ref(nias_map_concept(
      nias_get(lsData, "public_private"),
      c(PUBLIC = "nias-cs:public", PRIVATE = "nias-cs:private"),
      "public/private classification"
    ))
  )
  res <- nias_add_if_present(res, "nias-o:additionalInfo", nias_get(lsData, "info_additional"))
  res
}

dataParameterMonitoring_toFluree <- function(lsData) {
  monitored_or_fixed <- nias_map_concept(
    nias_get(lsData, "monitored_or_fixed"),
    c(MONITORED = "nias-cs:monitored", FIXED_EXANTE = "nias-cs:fixed-ex-ante", FIXED_EX_ANTE = "nias-cs:fixed-ex-ante"),
    "monitored or fixed"
  )
  res <- list(
    "@context" = nias_context(),
    "@type" = "nias-o:DataParameterRequirement",
    "rdfs:label" = nias_get(lsData, "label"),
    "schema:description" = nias_get(lsData, "description"),
    "nias-o:dataParameterPurpose" = nias_get(lsData, "purpose"),
    "ind:hasUnit" = nias_ref(nias_unit_iri(nias_get(lsData, "unit_of_measure"))),
    "nias-o:monitoredOrFixed" = nias_ref(monitored_or_fixed)
  )
  if (monitored_or_fixed == "nias-cs:fixed-ex-ante") {
    res <- nias_add_if_present(res, "nias-o:parameterAppliedValue", nias_numeric(nias_get(lsData, "value_applied")))
    res <- nias_add_if_present(res, "nias-o:dataSource", nias_get(lsData, "data_source"))
  } else {
    res <- nias_add_if_present(res, "nias-o:measurementMethodsAndProcedures", nias_get(lsData, "measurement_methods_and_procedures"))
    res <- nias_add_if_present(res, "nias-o:qaQcProcedures", nias_get(lsData, "qa_qc_procedures"))
    res <- nias_add_if_present(res, "nias-o:monitoringFrequency", nias_get(lsData, "monitoring_frequency"))
    res <- nias_add_if_present(res, "nias-o:samplingPlan", nias_get(lsData, "sampling_plan"))
  }
  res
}

sImpact_3x0x0_toFluree <- function(lsData, projectId) {
  is_unmonitored <- nias_enum(nias_get(lsData, "monitored")) == "NO"
  res <- list(
    "@context" = nias_context(),
    "@type" = "impactont:Impact",
    "nias-o:impactIntentionality" = nias_ref(nias_map_concept(
      nias_get(lsData, "intentionality"),
      c(INTENTIONAL = "nias-cs:intentional", UNINTENTIONAL = "nias-cs:unintentional"),
      "impact intentionality"
    )),
    "nias-o:beneficialOrAdverse" = nias_ref(nias_map_concept(
      nias_get(lsData, "beneficial_or_adverse"),
      c(BENEFICIAL = "nias-cs:beneficial", ADVERSE = "nias-cs:adverse"),
      "beneficial or adverse"
    )),
    "schema:description" = nias_get(lsData, "description"),
    "nias-o:monitored" = nias_ref(nias_yes_no_concept(nias_get(lsData, "monitored")))
  )
  if (is_unmonitored) {
    res <- nias_add_if_present(res, "nias-o:notMonitoredJustification", nias_get(lsData, "not_monitored_justification"))
    return(res)
  }

  indicator <- indicator_toFluree(
    lbl = nias_get(lsData, "indicator_label"),
    uom = nias_get(lsData, "indicator_unit_of_measure"),
    indicatorId = nias_get(lsData, "indicator_id"),
    description = nias_get(lsData, "indicator")
  )
  crediting_period <- nias_get(lsData, "crediting_period")
  res[["nias-o:additionalityJustification"]] <- nias_get(lsData, "additionality")
  res[["impactont:hasStateA"]] <- state_toFluree(
    dtStart = nias_get(crediting_period, "datetime_start"),
    dtEnd = nias_get(crediting_period, "datetime_end"),
    mod = "counterfactual",
    indic = indicator,
    indicId = NULL,
    val = nias_get(lsData, "state_baseline")
  )
  res[["impactont:hasStateB"]] <- state_toFluree(
    dtStart = nias_get(crediting_period, "datetime_start"),
    dtEnd = nias_get(crediting_period, "datetime_end"),
    mod = "real",
    indic = indicator,
    indicId = NULL,
    val = nias_get(lsData, "state_project")
  )
  res[["impactont:hasProvenance"]] <- nias_ref(nias_project_iri(projectId))
  res[["nias-o:monitoringPeriod"]] <- lapply(nias_rows(nias_get(lsData, "monitoring_periods")), function(p) {
    dateTimePeriod_toFluree(start = nias_get(p, "datetime_start"), end = nias_get(p, "datetime_end"))
  })
  res[["nias-o:creditingPeriod"]] <- creditingPeriod_toFluree(
    start = nias_get(crediting_period, "datetime_start"),
    end = nias_get(crediting_period, "datetime_end"),
    renewable = nias_enum(nias_get(lsData, "crediting_period_type")) == "RENEWABLE"
  )
  res <- nias_add_if_present(res, "nias-o:exAnteImpactEstimate", nias_numeric(nias_get(lsData, "impact_estimation_ex_ante")))
  data_parameters <- lapply(nias_rows(nias_get(lsData, "data_and_parameters")), dataParameterMonitoring_toFluree)
  if (length(data_parameters) > 0) {
    res[["nias-o:dataParameterRequirement"]] <- data_parameters
  }
  res
}

impactClaim_toFluree <- function(lsData, projectId) {
  methods <- nias_rows(nias_get(lsData, "methodologies"))
  if (length(methods) == 0) {
    return(NULL)
  }
  method_refs <- lapply(methods, function(m) {
    method <- nias_get(m, "methodology", m)
    sMethodology_1x0x0_toFluree(
      title = nias_get(method, "title"),
      label = nias_get(method, "label"),
      versionTag = nias_get(method, "version"),
      methodologyId = nias_get(method, "id")
    )
  })
  res <- list(
    "@context" = nias_context(),
    "@type" = "aiao:ImpactClaim",
    "claimont:hasSubject" = nias_ref(nias_project_iri(projectId)),
    "nias-o:usesMethodology" = method_refs
  )
  applicability <- vapply(methods, function(m) {
    value <- nias_get(m, "applicability")
    if (nias_has_value(value)) as.character(value) else NA_character_
  }, character(1))
  applicability <- applicability[!is.na(applicability)]
  if (length(applicability) > 0) {
    res[["nias-o:additionalInfo"]] <- paste(applicability, collapse = "\n")
  }
  res
}

sPDDxA_1x0x0_toFluree <- function(lsData) {
  headers <- nias_get(lsData, "headers")
  project_id <- nias_get(headers, "id_subject")
  res <- list(
    "@context" = nias_context(),
    "@id" = nias_project_iri(project_id),
    "@type" = "aiao:Project",
    "nias-o:title" = nias_get(lsData, "title_project"),
    "aiao:hasObjective" = list(
      "@type" = "aiao:Objective",
      "schema:description" = nias_get(lsData, "purpose_project")
    ),
    "impactont:hasSpatialLocation" = lapply(nias_rows(nias_get(lsData, "location_project")), function(x) {
      list(
        "@type" = c("impactont:SpatialLocation", "dcterms:Resource"),
        "nias-o:resourceIpfsUri" = nias_any_uri_literal(x)
      )
    }),
    "nias-o:technologyOrMeasure" = lapply(nias_rows(nias_get(lsData, "techmeas_project")), sTechnologyOrMeasure_1x0x0_toFluree),
    "nias-o:projectParty" = lapply(nias_rows(nias_get(lsData, "parties_project")), projectParty_toFluree),
    "nias-o:legalMatters" = nias_get(lsData, "legal_matters"),
    "nias-o:publicFundingStatus" = nias_ref(nias_yes_no_concept(nias_get(lsData, "status_public_funding"))),
    "nias-o:projectHistory" = nias_get(lsData, "history_project"),
    "nias-o:debundlingAssessment" = nias_get(lsData, "debundling")
  )
  sources <- nias_rows(nias_get(lsData, "source_public_funding"))
  if (length(sources) > 0) {
    res[["nias-o:publicFundingSource"]] <- unlist(sources, use.names = FALSE)
  }
  res <- nias_add_if_present(res, "nias-o:eligibilityDescription", nias_get(lsData, "eligibility_project"))
  res
}

sPDDxB_9x0x0_toFluree <- function(lsData, projectId = NULL) {
  headers <- nias_get(lsData, "headers")
  if (!nias_has_value(projectId)) {
    projectId <- nias_get(headers, "id_subject")
  }
  impact_rows <- nias_rows(nias_get(lsData, "impacts"))
  claims <- lapply(impact_rows, impactClaim_toFluree, projectId = projectId)
  claims <- Filter(Negate(is.null), claims)
  res <- list(
    "@context" = nias_context(),
    "@id" = paste0("nias-o:impact-declarations/", nias_slug(projectId)),
    "@type" = "nias-o:ImpactDeclaration",
    "claimont:hasSubject" = nias_ref(nias_project_iri(projectId)),
    "nias-o:hasDeclaredImpact" = lapply(impact_rows, sImpact_3x0x0_toFluree, projectId = projectId)
  )
  if (length(claims) > 0) {
    res[["nias-o:impactClaim"]] <- claims
  }
  res
}

hederaTopicMessage_toFluree <- function(messageId = NULL, topicId = NULL, sequenceNumber = NULL, consensusTimestamp = NULL) {
  if (nias_has_value(messageId) && (!nias_has_value(topicId) || !nias_has_value(consensusTimestamp))) {
    parts <- strsplit(as.character(messageId), "-", fixed = TRUE)[[1]]
    if (length(parts) >= 1 && grepl("^\\d+\\.\\d+\\.\\d+$", parts[[1]]) && !nias_has_value(topicId)) {
      topicId <- parts[[1]]
    }
    if (length(parts) >= 3 && !nias_has_value(consensusTimestamp)) {
      seconds <- suppressWarnings(as.numeric(parts[[2]]))
      nanos <- suppressWarnings(as.integer(parts[[3]]))
      if (!is.na(seconds) && !is.na(nanos)) {
        base_time <- format(as.POSIXct(seconds, origin = "1970-01-01", tz = "UTC"), "%Y-%m-%dT%H:%M:%S", tz = "UTC")
        consensusTimestamp <- sprintf("%s.%09dZ", base_time, nanos)
      }
    }
  }
  message_slug <- nias_slug(paste(topicId, sequenceNumber, consensusTimestamp, messageId, sep = "-"))
  res <- list(
    "@context" = nias_context(),
    "@id" = paste0("nias-o:hedera-topic-messages/", message_slug),
    "@type" = "hedera:TopicMessage"
  )
  if (nias_has_value(topicId)) {
    res[["hedera:inTopic"]] <- list(
      "@type" = "hedera:ConsensusTopic",
      "hedera:hasTopicId" = as.character(topicId)
    )
  }
  res <- nias_add_if_present(res, "hedera:hasSequenceNumber", if (nias_has_value(sequenceNumber)) as.integer(sequenceNumber) else NULL)
  res <- nias_add_if_present(res, "hedera:hasConsensusTimestamp", if (nias_has_value(consensusTimestamp)) nias_datetime_literal(consensusTimestamp) else NULL)
  res <- nias_add_if_present(res, "hedera:hasMessageContent", messageId)
  res
}

workflowDocumentMetadata_toFluree <- function(docId = NULL, dfDocMd = NULL, dbCon = NULL) {
  if (!nias_has_value(docId) && !nias_has_value(dfDocMd)) {
    stop("Must provide either docId or dfDocMd.")
  }
  if (!nias_has_value(dfDocMd)) {
    dfDocMd <- dbGetQuery(
      conn = dbCon,
      statement = sprintf("SELECT * FROM tbl_document_metadata WHERE id = '%s';", docId)
    )
  }
  if (!nias_has_value(docId)) {
    docId <- nias_get(dfDocMd, "id")
  }
  did_author <- nias_get(dfDocMd, "did_author")
  id_author <- nias_get(dfDocMd, "id_author")
  if (!nias_has_value(id_author) && nias_has_value(dbCon) && nias_has_value(did_author)) {
    id_author <- dbGetQuery(
      conn = dbCon,
      statement = sprintf("SELECT id_agent FROM tbl_link_agents_x_dids WHERE did = '%s';", did_author)
    )[["id_agent"]]
  }
  if (!nias_has_value(id_author)) {
    id_author <- nias_slug(did_author, fallback = "unknown-author")
  }
  author_ref <- list("@id" = nias_agent_iri(id_author), "@type" = "nias-o:PlatformUser")
  recipient_id <- nias_get(dfDocMd, "id_recipient")
  if (!nias_has_value(recipient_id)) {
    recipient_id <- "platform"
  }
  recipient_ref <- list("@id" = nias_agent_iri(recipient_id), "@type" = "infocomm:CommunicationParty")
  doc_iri <- nias_document_iri(docId)
  res <- list(
    "@context" = nias_context(),
    "@id" = doc_iri,
    "@type" = "data:Document",
    "nias-o:resourceIpfsUri" = nias_any_uri_literal(nias_get(dfDocMd, "uri_ipfs")),
    "nias-o:documentSchema" = nias_ref(paste0("nias-o:document-schema/", nias_get(dfDocMd, "id_schema"))),
    "nias-o:isEncrypted" = as.logical(nias_get(dfDocMd, "encrypted")),
    "nias-o:documentAuthor" = author_ref,
    "nias-o:authProof" = nias_ref(nias_map_concept(
      nias_get(dfDocMd, "type_doc"),
      c(REGULAR_UNSIGNED = "nias-cs:none", REGULAR_SIGNED = "nias-cs:eddsa-signature", VC = "nias-cs:vc"),
      "document auth proof"
    )),
    "nias-o:hasWorkflowSubmission" = list(
      "@type" = "nias-o:WorkflowDocumentSubmission",
      "nias-o:submittedDocument" = nias_ref(doc_iri),
      "nias-o:workflow" = list(
        "@id" = paste0("nias-o:workflows/", nias_get(dfDocMd, "id_workflow")),
        "@type" = "nias-o:Workflow"
      ),
      "nias-o:workflowStep" = list(
        "@type" = "nias-o:WorkflowStep",
        "rdfs:label" = as.character(nias_get(dfDocMd, "step_workflow"))
      ),
      "nias-o:workflowSubject" = nias_ref(nias_project_iri(nias_get(dfDocMd, "id_entity"))),
      "nias-o:workflowDocumentSubmittedBy" = author_ref,
      "nias-o:workflowDocumentRecipient" = recipient_ref,
      "nias-o:workflowSubmissionConsensusMessage" = hederaTopicMessage_toFluree(
        messageId = nias_get(dfDocMd, "id_message_h"),
        topicId = nias_get(dfDocMd, "id_topic_h"),
        sequenceNumber = nias_get(dfDocMd, "sequence_number_h"),
        consensusTimestamp = nias_get(dfDocMd, "consensus_timestamp_h")
      )
    )
  )
  res
}

sAgentDetails_1x0x0_toFluree <- function(agentId, lsData) {
  list(
    "@context" = nias_context(),
    "@type" = c("aiao:Agent", "nias-o:PlatformUser"),
    "@id" = nias_agent_iri(agentId),
    "schema:givenName" = nias_get(lsData, "name_first"),
    "schema:familyName" = nias_get(lsData, "name_last"),
    "schema:birthDate" = nias_get(lsData, "date_of_birth"),
    "schema:nationality" = nias_get(lsData, "country")
  )
}
