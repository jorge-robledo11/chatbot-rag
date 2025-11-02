import asyncio
from backend.src.infrastructure import get_infrastructure
from backend.src.services.scraper_service import ScraperService
from loguru import logger
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

async def main():
    """
    Orquesta el pipeline de scraping e indexación web siguiendo estos pasos:
    1.  Inicialización: Configura los clientes de infraestructura y servicios de scraping.
    2.  Extracción Web: Ejecuta el scraping de fuentes predefinidas con reglas de filtrado.
    3.  Procesamiento: Convierte los datos scraped a documentos estructurados con IDs determinísticos.
    4.  Enriquecimiento: Genera embeddings vectoriales para el contenido de cada documento.
    5.  Indexación: Sube los documentos enriquecidos al índice de búsqueda web de Azure.
    6.  Finalización: Cierra conexiones externas para liberar recursos.
    """
    # ------------------------------------------------------------------------------------------
    #                           🔧 FASE 1: INICIALIZACIÓN DE DEPENDENCIAS 🔧
    # ------------------------------------------------------------------------------------------
    logger.info("🚀 Iniciando pipeline de scraping e indexación web...")
    infra = get_infrastructure()
    
    # Configuración del servicio de scraping
    scraper_config = {
        "llm": {
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "model": "azure_openai/gpt-4o",
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION")
        },
        "verbose": False,
        "headless": True,
    }
    
    # Fuentes y reglas de procesamiento
    sources = {
        "sobre ajover": "https://www.ajover.com/sobre-ajover/",
        "sostenibilidad": "https://www.ajover.com/sostenibilidad/",
        "noticias": "https://www.ajover.com/noticias/",
        "proyectos": "https://www.ajover.com/proyectos/",
        "gana ajover": "https://www.ajover.com/gana-ajover/",
        'match': 'https://www.ajover.com/noticia/crea-match-perfectos-con-la-mejor-calidad-ajover/',
        'aumentar ventas': 'https://www.ajover.com/noticia/aumenta-tus-ventas-con-nuestra-cubierta-termoacustica/',
        'renovar espacios': 'https://www.ajover.com/noticia/renueva-los-espacios-y-que-tu-hogar-sea-tu-lugar-favorito/',
        'construccion sostenible': 'https://www.ajover.com/noticia/ajover-se-une-al-consejo-colombiano-de-construccion-sostenible/'
    }
    mantener = {"Contacto", "Copyright"}
    eliminar = {
        "Línea Ética", "Politica de tratamiento de datos", 'Bodega Inducol', 
        'Urbanización San Carlos II', 'Suscríbete a nuestro newsletter', 'Links relevantes', 
        'Casa Campestre Delicias', 'Casa Campestre Villa Leo', 'Casa residencial', 
        'Casa Campestre Delicias',
    }
    prioridad = ["sobre_ajover", "sostenibilidad", "noticias", "proyectos", 'gana_ajover']

    # Inicialización del scraper con configuración
    scraper = ScraperService(
        config=scraper_config,
        sources=sources,
        mantener=mantener,
        eliminar=eliminar,
        prioridad=prioridad
    )

    # ------------------------------------------------------------------------------------------
    #                           🌐 FASE 2: EXTRACCIÓN WEB (SCRAPING) 🌐
    # ------------------------------------------------------------------------------------------
    logger.info("🚀 Ejecutando scraping de fuentes web...")
    dict_preprocesado = await scraper.run_scraper()
    logger.success("✅ Scraping completado. Datos obtenidos: {} páginas", len(dict_preprocesado))

    # ------------------------------------------------------------------------------------------
    #                       🛠️ FASE 3: PROCESAMIENTO DE DOCUMENTOS 🛠️
    # ------------------------------------------------------------------------------------------
    logger.info("Convirtiendo datos scraped a documentos estructurados...")
    docs = scraper.convertir_a_documentos_web(dict_preprocesado)
    logger.debug("Documentos generados: {}", [doc["id"] for doc in docs])

    # ------------------------------------------------------------------------------------------
    #                       🔍 FASE 4: ENRIQUECIMIENTO CON EMBEDDINGS 🔍
    # ------------------------------------------------------------------------------------------
    openai_service = await infra.get_openai()
    search_ai = await infra.get_searchai(index_type="web")
    await search_ai.create_index_if_not_exists()

    logger.info("Generando embeddings para {} documentos...", len(docs))
    for doc in docs:
        doc["content_vector"] = await openai_service.get_text_embedding(doc["content"])
    logger.success("✅ Embeddings generados para todos los documentos")

    # ------------------------------------------------------------------------------------------
    #                       📥 FASE 5: INDEXACIÓN EN AZURE SEARCH 📥
    # ------------------------------------------------------------------------------------------
    logger.info("Subiendo documentos al índice web...")
    allowed = {"id", "title", "content", "source", "source_url", "content_vector"}
    docs = [{k: v for k, v in d.items() if k in allowed} for d in docs]
    await search_ai.upload_documents_batch(docs)
    logger.success("🎉 Indexación completada. Documentos indexados: {}", len(docs))

    # ------------------------------------------------------------------------------------------
    #                           🔌 FASE 6: CIERRE DE CONEXIONES 🔌
    # ------------------------------------------------------------------------------------------
    logger.info("Liberando recursos...")
    await infra.shutdown()
    logger.success("✅ Pipeline finalizado. Recursos liberados")

if __name__ == "__main__":
    asyncio.run(main())
