"""
Sistema de profiling avanzado para agentes RAG e infraestructura.

- Un único decorador `@profile` para medir latencia, CPU y memoria.
- Genera únicamente JSON de métricas.
- Soporta funciones síncronas y asíncronas.
"""

import cProfile
import functools
import inspect
import json
import pstats
import time
import tracemalloc
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

from loguru import logger

try:
    import psutil
except ModuleNotFoundError:
    psutil = None


@dataclass
class PerformanceMetrics:
    """Modelo de datos para almacenar las métricas de profiling."""

    function_name: str
    execution_time: float
    cpu_percent: float
    memory_peak_mb: float
    memory_current_mb: float
    call_count: int
    tokens_processed: int | None = None
    context_size: int | None = None
    timestamp: float = 0.0


class CoreProfiler:
    """
    Profiler central que guarda métricas y genera JSON por función.

    - Un único decorador `@profile` para medir latencia, CPU y memoria.
    - Genera únicamente JSON de métricas.
    - Soporta funciones síncronas y asíncronas.
    """

    def __init__(self, output_dir: Path = Path('performance')) -> None:
        """
        Inicializa el profiler central.

        Args:
            output_dir (Path): Directorio para guardar los archivos de métricas.
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.metrics: list[PerformanceMetrics] = []
        self.session_start = time.time()
        logger.debug(
            f"Profiler inicializado. Directorio de salida: '{self.output_dir}'."
        )

    def start_memory_tracking(self) -> None:
        """Inicia el tracking de memoria usando tracemalloc."""
        logger.info('Iniciando monitoreo de memoria con tracemalloc.')
        tracemalloc.start()

    def stop_memory_tracking(self) -> None:
        """Detiene el tracking de memoria usando tracemalloc."""
        logger.info('Deteniendo monitoreo de memoria con tracemalloc.')
        tracemalloc.stop()

    @contextmanager
    def profile_sync(
        self,
        function_name: str,
        context: dict[str, object],
    ) -> Generator[cProfile.Profile, None, None]:
        """
        Mide una función síncrona.

        Args:
            function_name (str): Nombre de la función.
            context (dict[str, object]): Contexto adicional para métricas.

        Yields:
            Generator[cProfile.Profile, None, None]: Context manager para profiling.
        """
        logger.debug(f'Profiling síncrono iniciado para: {function_name}')
        start = time.time()

        if psutil:
            proc = psutil.Process()
            cpu_start = proc.cpu_percent()
            mem_start = proc.memory_info().rss / 1024**2
        else:
            cpu_start = mem_start = 0.0

        prof = cProfile.Profile()
        prof.enable()
        try:
            yield prof
        finally:
            prof.disable()
            from_stats = pstats.Stats(prof)
            call_count = sum(ncalls for ncalls, *_ in from_stats.stats.values())
            metric = self._collect_metrics(
                function_name,
                start,
                cpu_start,
                mem_start,
                call_count,
                context,
            )
            self.metrics.append(metric)
            self._write_json(metric)
            logger.info(
                f'Profiling síncrono finalizado para: {function_name}. Tiempo: {metric.execution_time:.3f}s, Memoria pico: {metric.memory_peak_mb:.2f}MB, Llamadas: {metric.call_count}'
            )

    @asynccontextmanager
    async def profile_async(
        self,
        function_name: str,
        context: dict[str, object],
    ) -> AsyncGenerator[cProfile.Profile, None]:
        """
        Mide una función asíncrona.

        Args:
            function_name (str): Nombre de la función.
            context (dict[str, object]): Contexto adicional para métricas.

        Yields:
            AsyncGenerator[cProfile.Profile, None]: Context manager para profiling.
        """
        logger.debug(f'Profiling asíncrono iniciado para: {function_name}')
        start = time.time()

        if psutil:
            proc = psutil.Process()
            cpu_start = proc.cpu_percent()
            mem_start = proc.memory_info().rss / 1024**2
        else:
            cpu_start = mem_start = 0.0

        prof = cProfile.Profile()
        prof.enable()
        try:
            yield prof
        finally:
            prof.disable()
            from_stats = pstats.Stats(prof)
            call_count = sum(ncalls for ncalls, *_ in from_stats.stats.values())
            metric = self._collect_metrics(
                function_name,
                start,
                cpu_start,
                mem_start,
                call_count,
                context,
            )
            self.metrics.append(metric)
            self._write_json(metric)
            logger.info(
                f'Profiling asíncrono finalizado para: {function_name}. Tiempo: {metric.execution_time:.3f}s, Memoria pico: {metric.memory_peak_mb:.2f}MB, Llamadas: {metric.call_count}'
            )

    def _collect_metrics(
        self,
        function_name: str,
        start: float,
        cpu_start: float,
        mem_start: float,
        call_count: int,
        context: dict[str, object],
    ) -> PerformanceMetrics:
        """
        Reúne todas las métricas en un objeto.

        Args:
            function_name (str): Nombre de la función.
            start (float): Tiempo inicial.
            cpu_start (float): Uso de CPU inicial.
            mem_start (float): Memoria inicial.
            call_count (int): Cantidad de llamadas.
            context (dict[str, object]): Contexto adicional.

        Returns:
            PerformanceMetrics: Objeto de métricas.
        """
        end = time.time()

        if psutil:
            proc = psutil.Process()
            cpu_end = proc.cpu_percent()
            mem_now = proc.memory_info().rss / 1024**2
        else:
            cpu_end = mem_now = 0.0

        peak = mem_start
        if tracemalloc.is_tracing():
            _, peak_bytes = tracemalloc.get_traced_memory()
            peak = peak_bytes / 1024**2

        logger.debug(
            f'[{function_name}] Métricas recogidas: tiempo={end - start:.4f}s, cpu={cpu_end - cpu_start:.2f}%, memoria_actual={mem_now:.2f}MB, memoria_pico={peak:.2f}MB, llamadas={call_count}'
        )

        return PerformanceMetrics(
            function_name=function_name,
            execution_time=end - start,
            cpu_percent=cpu_end - cpu_start,
            memory_peak_mb=peak,
            memory_current_mb=mem_now,
            call_count=call_count,
            tokens_processed=context.get('tokens'),
            context_size=context.get('context_size'),
            timestamp=end,
        )

    def _write_json(self, metric: PerformanceMetrics) -> None:
        """
        Escribe o sobrescribe el archivo JSON de la función.

        Args:
            metric (PerformanceMetrics): Métricas a guardar.
        """
        path = self.output_dir / f'{metric.function_name}.json'
        try:
            path.write_text(json.dumps(asdict(metric), indent=2))
            logger.debug(f'Archivo de métricas guardado: {path}')
        except PermissionError as e:
            logger.warning(
                f'No se pudo escribir JSON de perfil `{metric.function_name}`: {e}'
            )

    def generate_report(self) -> dict[str, object]:
        """
        Crea resumen de métricas acumuladas.

        Returns:
            dict[str, object]: Reporte de resumen.
        """
        logger.debug('Generando reporte global de métricas de profiling.')
        if not self.metrics:
            logger.warning('No hay métricas recolectadas para generar el reporte.')
            return {'error': 'no metrics'}
        grouped: dict[str, list[PerformanceMetrics]] = {}
        for m in self.metrics:
            grouped.setdefault(m.function_name, []).append(m)

        report: dict[str, object] = {
            'session_duration': time.time() - self.session_start,
            'total_calls': len(self.metrics),
            'functions': {},
        }
        for fn, lst in grouped.items():
            avg_t = sum(x.execution_time for x in lst) / len(lst)
            max_t = max(x.execution_time for x in lst)
            avg_mem = sum(x.memory_peak_mb for x in lst) / len(lst)
            report['functions'][fn] = {
                'count': len(lst),
                'avg_time': avg_t,
                'max_time': max_t,
                'avg_memory_peak_mb': avg_mem,
            }
        logger.info(
            f'Reporte global generado para {len(report["functions"])} funciones.'
        )
        return report

    def save_report(self, filename: str | None = None) -> Path:
        """
        Guarda el reporte JSON global en disco.

        Args:
            filename (str | None): Nombre de archivo para el reporte.

        Returns:
            Path: Ruta del archivo generado.
        """
        report = self.generate_report()
        if filename is None:
            filename = 'performance_summary.json'
        path = self.output_dir / filename
        try:
            path.write_text(json.dumps(report, indent=2))
            logger.info(f'Reporte global de métricas guardado: {path}')
        except PermissionError as e:
            logger.warning(f'No se pudo escribir resumen JSON: {e}')
        return path


profiler = CoreProfiler()


def profile(
    function_name: str,
    tokens: int | None = None,
    context_size: int | None = None,
) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Decorador para medir rendimiento. Detecta si la función es async o sync.

    Args:
        function_name (str): Nombre de la función.
        tokens (int | None): Cantidad de tokens procesados (opcional).
        context_size (int | None): Tamaño del contexto (opcional).

    Returns:
        Callable: Decorador parametrizado.
    """

    def decorator(fn: Callable[..., object]) -> Callable[..., object]:
        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def wrapped(*args: object, **kwargs: object) -> object:
                logger.debug(f'Llamada a función async perfilada: {function_name}')
                async with profiler.profile_async(
                    function_name, {'tokens': tokens, 'context_size': context_size}
                ):
                    return await fn(*args, **kwargs)

            return wrapped

        @functools.wraps(fn)
        def wrapped(*args: object, **kwargs: object) -> object:
            logger.debug(f'Llamada a función sync perfilada: {function_name}')
            with profiler.profile_sync(
                function_name, {'tokens': tokens, 'context_size': context_size}
            ):
                return fn(*args, **kwargs)

        return wrapped

    return decorator
