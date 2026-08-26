import os
import torch
from ultralytics import YOLO
from Core.utils import resource_path


class ModelManager:
    """
    Central manager for AI object detection models.
    Supports caching, dynamic switching between models (YOLO11n, Drone Detector),
    device detection (CUDA/CPU), and safe error handling.
    """

    MODEL_CONFIGS = {
        "YOLO11n": "yolo11n.pt",
        "Drone Detector": os.path.join("AI_training", "Models", "drone_best.pt"),
    }

    def __init__(self):
        self._cached_models = {}
        self._active_model_name = "YOLO11n"
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[ModelManager] Device initialized: {self._device.upper()}")

    def get_device_name(self) -> str:
        """Returns uppercase device string, e.g. 'CUDA' or 'CPU'."""
        if torch.cuda.is_available():
            try:
                return torch.cuda.get_device_name(0)
            except Exception:
                return "CUDA"
        return "CPU"

    def get_device(self) -> str:
        return self._device

    def get_active_model_name(self) -> str:
        return self._active_model_name

    def load_model(self, model_name: str):
        """
        Loads and caches the specified model name.
        Returns the loaded YOLO model instance.
        Raises FileNotFoundError or RuntimeError if loading fails.
        """
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(f"Unknown model name: {model_name}. Available: {list(self.MODEL_CONFIGS.keys())}")

        if model_name in self._cached_models:
            self._active_model_name = model_name
            return self._cached_models[model_name]

        rel_path = self.MODEL_CONFIGS[model_name]
        abs_path = resource_path(rel_path)

        if not os.path.exists(abs_path):
            # Fallback check if path was relative to project root
            if os.path.exists(rel_path):
                abs_path = rel_path
            else:
                raise FileNotFoundError(
                    f"Model file not found for '{model_name}'. Expected path: {abs_path}"
                )

        try:
            print(f"[ModelManager] Loading model '{model_name}' from: {abs_path}")
            model = YOLO(abs_path)
            model.to(self._device)
            self._cached_models[model_name] = model
            self._active_model_name = model_name
            print(f"[ModelManager] Model '{model_name}' loaded successfully on {self._device.upper()}")
            return model
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model '{model_name}': {str(e)}")

    def get_active_model(self):
        """
        Returns the currently active YOLO model object.
        Loads default 'YOLO11n' if no model is loaded yet.
        """
        if self._active_model_name in self._cached_models:
            return self._cached_models[self._active_model_name]

        return self.load_model(self._active_model_name)

    def is_model_loaded(self, model_name: str) -> bool:
        return model_name in self._cached_models
