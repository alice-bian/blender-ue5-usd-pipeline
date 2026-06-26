try:
    from crowd_diversity_pipeline import register, unregister
except ModuleNotFoundError:  # pragma: no cover - exercised when the package is loaded as a zip root
    from .crowd_diversity_pipeline import register, unregister

__all__ = ["register", "unregister"]
