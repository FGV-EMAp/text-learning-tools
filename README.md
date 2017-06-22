# text-learning-tools
Tools for OCR, data cleansing and Topic Modeling of texts.
Database: CPDOC's Antonio Azeredo da Silveira Collection, Subseries (Ministério de Relações Exteriores).

About the files in notebooks folder: 
* Tesseract_ocr: for OCR
* text_processing: for Data Cleansing
* text_processing-ignore_case: Second version of Data Cleansing which makes a database without CAPS correction. Used for entity extraction step.
* build_mysql_database_docs: Creates table with matadata about documents, such as id, content, main language, readability.
* build_mysql_database_dossies: Creates table with matadata about dossies (related with documents), such as subject, keywords, collection, url.
* clustering_lda_test_models: Testa parâmetros de modelagem de tópicos e usa dois modelos diferentes (LDA e HDP)
* clustering_lda_doc_topics_mysql: Creates table with data about topics, documents and topic modelling score
* clustering_lda_token_topics_mysql: Creates table with data about topics and tokens (TODO LIST!)
* doc_entities_person_names_list.ipynb: Creates person gazeteers for extraction
* doc_entities_person_extract_and_store.ipynb: Data Mining for entities/persons
* doc_entities_country: Data Mining for entities/countries
* doc_entities_person-id_adjustment: small adjustments on persons ids
* mysql_database_update_dates: adjustments on dates of documents
* doc_entities_vis: Makes some basic visualization (draft)
* doc_entities_vis_graph: Builds data for visualization with graphs

Also, we have organization tools in cpdoc-file-organization folder, that we used to reorder and rename CPDOC files.
They are listed by the order they were used:
* file_error_identifier: script que identifica arquivos com nome errado devido a quebra de sequência.
* file_rename-to_tif: renomeia arquivos txt para o formato de nome de arquivos tif.
* file_comparison_txt_tif: seleciona e separa arquivos tif e txt em uma mesma pasta para analisá-los ou compará-los.
* file_rename-to_doc: renomeia arquivos txt ou tif para o formato de nome de documentos.
* file_comparison_doc: seleciona e separa arquivos tif (ou txt) em uma mesma pasta para analisá-los ou compará-los com documentos.
* file_group-by_doc: reagrupa arquivos txt para que cada arquivo represente um documento. Antes eram divididos por páginas de documentos.
* file_manager_doc_topics: Captura id de 20 documentos de maior score por tópicos selecionados, cria cóía dos mesmos em pastas separadas e cria tabela em Excel com meta-dados para análise posterior de validação dos tópicos gerados.