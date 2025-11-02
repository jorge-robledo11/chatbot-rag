"""
Servicio de scraping web con procesamiento inteligente de contenido.
"""

import asyncio
import hashlib
import re
from copy import deepcopy
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import unicodedata
from loguru import logger
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperMultiGraph

# Nota: seguimos importando tu helper por compatibilidad, pero para los IDs web
# usamos una función local en HEX para evitar claves inválidas en Azure.
from backend.src.utils.identity_utils import generate_deterministic_id  # noqa: F401


class ContenidoDinamico(BaseModel):
    """Esquema de salida del scraping por secciones."""
    contenido: dict[str, str] = Field(
        description=(
            "Las claves son los títulos de las secciones encontradas en la página. "
            "Los valores son los textos completos de cada sección, sin resumir."
        )
    )


def _norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().strip().replace(" ", "_").replace("-", "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s


def _canonicalize_url(u: str) -> str:
    if not u:
        return u
    p = urlparse(u)
    path = p.path.rstrip("/") or "/"
    drop = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid"}
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in drop]
    p2 = p._replace(netloc=p.netloc.lower(), path=path, query=urlencode(query, doseq=True))
    return urlunparse(p2)


def _norm_text(s: str | None) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def _sha1(s: str) -> str:
    return hashlib.sha1((s or "").encode("utf-8")).hexdigest()


def _hex_id(input_str: str, max_length: int = 40) -> str:
    """
    ID determinístico seguro para Azure Search: HEX de SHA-256 (0-9a-f).
    Nunca empieza por '_' ni '-' y evita caracteres no permitidos.
    """
    h = hashlib.sha256(input_str.encode("utf-8")).hexdigest()  # 64 chars
    return h[:max_length] or "0"


class ScraperService:
    """
    Servicio de scraping web con capacidades de procesamiento avanzado.
    """

    def __init__(self, config: dict, sources: dict, mantener: set, eliminar: set, prioridad: list) -> None:
        self.config = config
        self.sources = {_norm_name(k): v for k, v in (sources or {}).items()}
        self.mantener = mantener or set()
        self.eliminar = eliminar or set()
        self.prioridad = [_norm_name(x) for x in (prioridad or [])]

    async def scrape_and_process(self, name: str, url: str) -> tuple[str, dict]:
        """Extrae contenido de una URL específica usando ScrapeGraphAI."""
        prompt = (
            f"Analiza el contenido de la página {url} y extrae toda su información textual de manera estructurada. "
            "Identifica cada sección principal por sus encabezados (h1, h2, h3, etc.) "
            "y para cada sección, extrae TODO el texto literal y completo, sin resumir. "
            "Devuelve un objeto JSON conforme al esquema."
        )
        logger.info(f"Scrapeando '{name}' → {url}")
        scraper = SmartScraperMultiGraph(prompt=prompt, source=[url], config=self.config, schema=ContenidoDinamico)
        try:
            result = await asyncio.to_thread(scraper.run)
            contenido = None
            if hasattr(result, "contenido"):
                contenido = dict(result.contenido)
            elif isinstance(result, dict):
                contenido = result.get("contenido", result)

            if isinstance(contenido, dict):
                contenido = {k: _norm_text(v) for k, v in contenido.items()}
                contenido["url"] = _canonicalize_url(url)
                logger.success(f"✅ Scraping OK: '{name}'")
                return name, contenido

            logger.error(f"Formato inesperado en '{name}': {type(result)}")
            return name, {"error": f"Formato inesperado: {type(result)}", "url": url}
        except Exception as e:
            logger.exception(f"Error al scrapear '{name}' ({url}): {e}")
            return name, {"error": str(e), "url": url}

    async def run_scraper(self) -> dict:
        """Scrapea todas las fuentes en paralelo y preprocesa resultados."""
        logger.info("Iniciando scraping paralelo de todas las fuentes…")
        tasks = [self.scrape_and_process(name, url) for name, url in self.sources.items()]
        resultados = await asyncio.gather(*tasks)
        results = dict(resultados)
        logger.info("Scraping completado. Preprocesando…")

        # Quita entradas con error
        results = {k: v for k, v in results.items() if isinstance(v, dict) and "error" not in v}
        dict_preprocesado = self._preprocesar(results)
        logger.success("✅ Preprocesamiento finalizado.")
        return dict_preprocesado

    def _preprocesar(self, results: dict) -> dict:
        """
        Reorganiza el contenido según 'mantener', 'eliminar' y 'prioridad'.
        """
        dict_preprocesado = deepcopy(results)

        # base_name = primera clave de prioridad presente
        base_name = next((n for n in self.prioridad if n in dict_preprocesado), None)
        if base_name is None:
            # fallback
            base_name = "sobre_ajover"
            dict_preprocesado.setdefault(base_name, {})

        # Paso 1: mover claves de 'mantener' a base_name
        for keep_key in self.mantener:
            for name, secciones in list(dict_preprocesado.items()):
                if name == base_name or not isinstance(secciones, dict):
                    continue
                if keep_key in secciones:
                    dict_preprocesado[base_name].setdefault(keep_key, secciones[keep_key])
                    del secciones[keep_key]

        # Paso 2: eliminar claves no deseadas
        for secciones in dict_preprocesado.values():
            if not isinstance(secciones, dict):
                continue
            for rm in self.eliminar:
                secciones.pop(rm, None)

        # Paso 3: deduplicar claves de sección por prioridad (mantener primer visto)
        vistos: set[str] = set()
        for name in self.prioridad:
            d = dict_preprocesado.get(name, {})
            if not isinstance(d, dict):
                continue
            for key in list(d.keys()):
                if key == "url":
                    continue
                if key in vistos:
                    del d[key]
                else:
                    vistos.add(key)

        # Limpieza: quita secciones vacías o con 'NA'
        for name, d in list(dict_preprocesado.items()):
            if not isinstance(d, dict):
                continue
            for k in list(d.keys()):
                if k == "url":
                    continue
                v = d[k]
                if v is None or _norm_text(v).upper() == "NA" or _norm_text(v) == "":
                    del d[k]
        return dict_preprocesado

    def convertir_a_documentos_web(self, dict_preprocesado: dict) -> list[dict]:
        """
        Convierte el contenido preprocesado a documentos para indexación Web.
        Output (para índice web híbrido): id, title, content, source, source_url
        * ID por sección: HEX(hash(url|título)) → válido para Azure.
        * Dedup por (source_url, title) y por contenido idéntico.
        """
        documentos: list[dict] = []

        for nombre_fuente, secciones in (dict_preprocesado or {}).items():
            if not isinstance(secciones, dict):
                continue
            url = secciones.get("url")

            for titulo, texto in secciones.items():
                if titulo == "url":
                    continue
                titulo_norm = _norm_text(titulo)
                texto_norm = _norm_text(texto)
                if not titulo_norm or not texto_norm or texto_norm.upper() == "NA":
                    continue

                # ID seguro para Azure (HEX). Evita claves con '_' inicial.
                doc_id = _hex_id(f"{url}|{titulo_norm}")

                documentos.append(
                    {
                        "id": doc_id,
                        "title": titulo_norm,
                        "content": texto_norm,
                        "source": nombre_fuente,      # normalizado
                        "source_url": url,            # nombre de campo correcto en el índice web
                    }
                )

        # Deduplicados por (source_url, title)
        seen_pair: set[tuple[str | None, str]] = set()
        uniq: list[dict] = []
        for d in documentos:
            key = (d.get("source_url"), d.get("title"))
            if key in seen_pair:
                continue
            seen_pair.add(key)
            uniq.append(d)

        # Dedup por contenido idéntico
        seen_hash: set[str] = set()
        uniq2: list[dict] = []
        for d in uniq:
            h = _sha1(d.get("content", ""))
            if h in seen_hash:
                continue
            seen_hash.add(h)
            uniq2.append(d)

        return uniq2
