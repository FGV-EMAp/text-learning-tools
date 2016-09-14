# text-learning-tools
Tools for OCR, cleaning and Topic Modeling of texts in portuguese.
Completed tasks  and to-do list:
* OCR (using tesseract python library)
* Data Cleansing (using re python library)
* Topic Modelling
* MapReduce
* Data Visualization

About the files in notebook folder, we have 
Tesseract_OCR: for OCR
processamento_textos: for Data Cleansing
Clustering_LDA: for Topic Modelling and Data Visualization

Also, we have organization tools in cpdoc-file-organization folder, that we used to reorder and rename CPDOC files.
They are listed by the order they were used:
*file_error_identifier: script que identifica arquivos com nome errado devido a quebra de sequência.
*file_rename-to_tif: renomeia arquivos txt para o formato de nome de arquivos tif.
*file_comparison_txt_tif: seleciona e separa arquivos tif e txt em uma mesma pasta para analisá-los ou compará-los.
*file_rename-to_doc: renomeia arquivos txt ou tif para o formato de nome de documentos.
*file_comparison_doc: seleciona e separa arquivos tif (ou txt) em uma mesma pasta para analisá-los ou compará-los com documentos.
*file_group-by_doc: reagrupa arquivos txt para que cada arquivo represente um documento. Antes eram divididos por páginas de documentos.
