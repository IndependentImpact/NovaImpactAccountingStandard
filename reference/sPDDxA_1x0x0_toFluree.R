sPDDxA_1x0x0_toFluree <- function(lsData) {
  
  res <- list(
    '@context' = list(
      "nias-o" = "https://nova.org.za/novaimpactaccountingstandard/",
      "schema" = "https://schema.org/",
      "aiao" = "https://w3id.org/aiao/",
      "impactont" = "https://w3id.org/impactont/",
      "dcterms" = "http://purl.org/dc/terms/"),
    
    '@id' = paste0("nias-o:activities/", lsData$headers$id_subject),
    
    '@type' = "aiao:Project",
    
    'nias-o:title' = lsData$title_project,
    'aiao:hasObjective' = list(
      '@type' = "aiao:Objective",
      'schema:description' = lsData$purpose_project),
    'impactont:hasSpatialLocation' = lapply(
      X = lsData$location_project, 
      FUN = function(x) {
        list('@type' = c("impactont:SpatialLocation", "dcterms:Resource"),
             'nias-o:resourceIpfsUri' = x)
      }),
    'nias-o:technologyOrMeasure' = lapply(
      X = lsData$techmeas_project, 
      FUN = sTechnologyOrMeasure_1x0x0_toFluree),
    'nias-o:projectHistory' = lsData$history_project)
  
  return(res)
}


# lsData <- getPubDoc(
#   docId = "66b658a5596f789333442dbaf66c7bbe",
#   dbCon = dbCon,
#   contentOnly = TRUE)
