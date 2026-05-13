sMethodology_1x0x0_toFluree <- function(title, label, versionTag) {
  
  res <- list(
    '@context' = list(
      "nias-o" = "https://nova.org.za/novaimpactaccountingstandard/",
      "dcterms" = "http://purl.org/dc/terms/",
      "rdfs" = "http://www.w3.org/2000/01/rdf-schema#",
      "data" = "http://jellyfiiish.xyz/ns/"),
    '@type' = "nias-o:Methodology",
    'dcterms:title' = title,
    'rdfs:label' = label,
    'data:versionTag' = versionTag)
  
  return(res)
  
}