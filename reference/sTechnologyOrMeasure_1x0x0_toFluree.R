
sTechnologyOrMeasure_1x0x0_toFluree <- function(lsData) {
  
  res <- list(
    '@context' = list(
      "nias-o" = "https://nova.org.za/novaimpactaccountingstandard/",
      "schema" = "https://schema.org/"),
    '@type' = "nias-o:TechnologyOrMeasure",
    'nias-o:techMeasType' = list(
      '@id' = switch(
        lsData$type_techmeas,
        FACILITY = "nias-o:facility",
        SYSTEM = "nias-o:system",
        EQUIPMENT = "nias-o:equipment",
        OTHER = "nias-o:other")),
    'schema:description' = lsData$description)

  if (length(jellyfi3shR::emptyOrMissingAsNull(lsData$age_current)) == 1) {
    res <- c(
      res, 
      list('nias-o:currentAgeInYears' = lsData$age_current))
  }
  
  if (length(jellyfi3shR::emptyOrMissingAsNull(lsData$lifespan_estimated)) == 1) {
    res <- c(
      res, 
      list('nias-o:estimatedLifespanInYears' = lsData$lifespan_estimated))
  }
  
  return(res)
  
}