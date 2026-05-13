creditingPeriod_toFluree <- function(start, end, renewable) {
  
  res <- list(
    '@context' = list(
      'time' = "http://www.w3.org/2006/time#",
      'nias-o' = "https://nova.org.za/novaimpactaccountingstandard/"),
    "@type" = "nias-o:CreditingPeriod",
    "time:hasBeginning" = list(
      "@type" = "time:Instant",
      "time:inXSDDateTimeStamp" = start),
    "time:hasEnd" = list(
      "@type" = "time:Instant",
      "time:inXSDDateTimeStamp" = end),
    "nias-o:creditingPeriodIsRenewable" = renewable)
  
  return(res)
  
}