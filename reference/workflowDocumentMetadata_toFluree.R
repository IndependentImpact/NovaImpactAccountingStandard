workflowDocumentMetadata_toFluree <- function(docId = NULL, dfDocMd = NULL, dbCon = NULL) {
  
  if (length(docId) == 0 & length(dfDocMd) == 0) {
    stop("Must provide either docId or dfDocMd.")
  }
  
  if (length(dfDocMd) == 0) {
    dfDocMd <- dbGetQuery(
      conn = dbCon,
      statement = sprintf(
        "SELECT * FROM tbl_document_metadata WHERE id = '%s';",
        docId))
  }
  if (length(docId) == 0) {
    docId <- dfDocMd$id
  }
  
  idAuthor <- dbGetQuery(
    conn = dbCon, 
    statement = sprintf(
      "SELECT id_agent FROM tbl_link_agents_x_dids WHERE did = '%s';",
      dfDocMd$did_author))[["id_agent"]]
  
  res <- list(
    '@context' = list(
      'data' = "http://jellyfiiish.xyz/ns/",
      'nias-o' = "https://nova.org.za/novaimpactaccountingstandard/",
      'rdfs' = "http://www.w3.org/2000/01/rdf-schema#"),
    
    '@id' = paste0("nias-o:documents/", docId),
    '@type' = "data:Document",
    
    'nias-o:resourceIpfsUri' = dfDocMd$uri_ipfs,
    'nias-o:documentSchema' = list(
      '@type' = "nias-o:DocumentSchema",
      '@id' = paste0("nias-o:document-schema/", dfDocMd$id_schema)),
    'nias-o:isEncrypted' = dfDocMd$encrypted, 
    'nias-o:documentAuthor' = list(
      '@id' = paste0("nias-o:agents/", idAuthor)),
    'nias-o:authProof' = list(
      '@id' = switch(
        dfDocMd$type_doc,
        REGULAR_UNSIGNED = "nias-o:none",
        REGULAR_SIGNED = "nias-o:eddsa-signature",
        VC = "nias-o:vc")),
    
    'nias-o:hasWorkflowSubmission' = list(
      '@type' = "nias-o:WorkflowDocumentSubmission",
      'nias-o:workflow' = list(
        '@id' = paste0("nias-o:workflows/", dfDocMd$id_workflow)),
      'nias-o:workflowStep' = list(
        '@type' = "nias-o:WorkflowStep",
        'rdfs:label' = dfDocMd$step_workflow),
      'nias-o:workflowSubject' = list(
        '@id' = paste0("nias-o:activities/", dfDocMd$id_entity)),
      'nias-o:workflowDocumentSubmissionHederaMessageId' = dfDocMd$id_message_h))
  
  return(res)
  
}