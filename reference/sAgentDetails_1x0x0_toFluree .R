
sAgentDetails_1x0x0_toFluree <- function(agentId, lsData) {
  
  res <- list(
    '@context' = list(
      'nias-o' = "https://nova.org.za/novaimpactaccountingstandard/",
      'schema' = "https://schema.org/",
      'aiao' = "http://w3id.org/aiao#"),
    '@type' = c("aiao:Agent", "nias-o:PlatformUser"),
    '@id' = paste0("nias-o:agents/", agentId),
    'schema:givenName' = lsData$name_first,
    'schema:familyName' = lsData$name_last,
    'schema:birthDate' = lsData$date_of_birth, 
    'schema:nationality' = lsData$country)
  
  return(res)
  
}
