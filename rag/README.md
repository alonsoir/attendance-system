Este directorio muestra experimentos sobre como tratar de usar la tecnica RAG.

No están pensados para producción, de hecho, creo que la técnica RAG tiene muchas fallas.

1)deep_research_terminal.py 

trata de usar multiples LLMs descritos en OPENROUTER_URL, puedes añadir mas si quieres, también trata de 
buscar en google, aunque probablemente Google te lo impedirá después de varios intentos. Genera un PDF.

2) advanced_rag.py

Hay que adaptarlo para que use PyPDF2, ahora mismo no funciona

3) advanced_rag_ray.py

experimento fallido, no se que ocurre, pero ray no se puede usar con el resto de frameworks debido a problemas de serializacion.

4)chat.py

Hay que adaptarlo para que use PyPDF2, ahora mismo no funciona. La idea es cargar los pdf de apoyo para que sirvan de
fuente para el RAG, además busca en internet.