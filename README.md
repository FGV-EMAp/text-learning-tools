# text-learning-tools
Tools for OCR, cleaning and Topic Modeling of texts in portuguese.
Completed tasks  and to-do list:
* OCR (using tesseract python library)
* Data Cleansing (using re python library)
* Topic Modelling
* MapReduce
* Data Visualization

About the files in notebook folder, we have 
* Tesseract_OCR: for OCR
* processamento_textos: for Data Cleansing
* build_mysql_database_docs: Creates table with matadata about documents, such as id, content, main language, readability.
* build_mysql_database_dossies: Creates table with matadata about dossies (related with documents), such as subject, keywords, collection, url.
* Clustering_LDA_test_models: Testa parâmetros de modelagem de tópicos e usa dois modelos diferentes (LDA e HDP)
* doc_topics: Creates table with data about topics, documents and topic modelling score
* doc_entities: Mineração de dados de entidades/pessoas
* doc_entities_country: Mineração de dados de entidades/países
* doc_entities_vis: Faz visualização de dados a partir das entidades (RASCUNHO)
* doc_entities_vis: Cria base de dados direcionada a posterior visualização em grafos
* Palavras_Snippet: Algoritmo de extração de entidades com o 'palavras'

Also, we have organization tools in cpdoc-file-organization folder, that we used to reorder and rename CPDOC files.
They are listed by the order they were used:
* file_error_identifier: script que identifica arquivos com nome errado devido a quebra de sequência.
* file_rename-to_tif: renomeia arquivos txt para o formato de nome de arquivos tif.
* file_comparison_txt_tif: seleciona e separa arquivos tif e txt em uma mesma pasta para analisá-los ou compará-los.
* file_rename-to_doc: renomeia arquivos txt ou tif para o formato de nome de documentos.
* file_comparison_doc: seleciona e separa arquivos tif (ou txt) em uma mesma pasta para analisá-los ou compará-los com documentos.
* file_group-by_doc: reagrupa arquivos txt para que cada arquivo represente um documento. Antes eram divididos por páginas de documentos.
* file_manager_doc_topics: Captura id de 20 documentos de maior score por tópicos selecionados, cria cóía dos mesmos em pastas separadas e cria tabela em Excel com meta-dados para análise posterior de validação dos tópicos gerados.