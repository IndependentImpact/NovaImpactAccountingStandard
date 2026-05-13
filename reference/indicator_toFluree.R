indicator_toFluree <- function(lbl, uom) {
  
  res <- list(
    '@context' = list(
      "nias-o" = "https://nova.org.za/novaimpactaccountingstandard/",
      "rdfs" = "http://www.w3.org/2000/01/rdf-schema#",
      "impactont" = "https://w3id.org/impactont/"),
    '@type' = "impactont:Indicator",
    'rdfs:label' = lbl,
    'nias-o:unitOfMeasure' = uom)
  
  return(res)
  
}