import hashlib
import json
import os
from typing import Dict, Optional, Callable, TypeVar

from pydantic import BaseModel

from const.const_gl import ConstGl

T = TypeVar('T', bound=BaseModel)

class ResultFileCache:
    def __init__(self, map_file: str = None):
        if map_file is None:
            map_file = os.path.join(ConstGl.TEMP_DIR, 'cache', 'result_hash_map.json')
        self.map_file = map_file
        self.hash_map: Dict[str, str] = self._load_hash_map()

    def _load_hash_map(self) -> Dict[str, str]:
        if os.path.exists(self.map_file):
            with open(self.map_file, "r") as file:
                return json.load(file)
        return {}

    def compute_hash(self, file_path: str) -> str:
        """Compute and return SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def update_hash_map(self, file_path: str, doc_data: BaseModel):
        """Update the hash map with the new hash and document data in JSON format."""
        file_hash = self.compute_hash(file_path)
        self.hash_map[file_hash] = doc_data.model_dump_json()
        self._save_hash_map()

    def _save_hash_map(self):
        parent_directory = os.path.dirname(self.map_file)
        os.makedirs(parent_directory, exist_ok=True)
        with open(self.map_file, "w") as file:
            json.dump(self.hash_map, file, indent=4)

    def clear_cache(self):
        self.hash_map = {}
        self._save_hash_map()

    def get_document_by_hash(self,
                             file_hash: str,
                             cls: type[BaseModel]
                             ) -> Optional[BaseModel]:
        """Retrieve document data by hash if available."""
        dumped_model = self.hash_map.get(file_hash)
        if dumped_model:
            return cls(**json.loads(dumped_model))
        return None


    def get_or_process_document(self,
                                file_path: str,
                                callback_process: Callable[[str], T],
                                found_callback: Optional[Callable[[T, str], None]] = None
                                ) -> T:
        """Retrieve document data by hash if available,
        When found call the found_callback with the document data and file path (useful to update the document path if renamed),
        otherwise process the document.

        Args:
            file_path (str): The path to the file.
            callback_process (Callable[[str], T]): The callback function to process the document.
            found_callback (Optional[Callable[[T, str], None]]): The callback function to call if the document is found.

        Returns:
            T: The document data.
        """
        file_hash = self.compute_hash(file_path)
        model_cls = callback_process.__annotations__['return']
        doc_data = self.get_document_by_hash(file_hash, model_cls)
        if doc_data:
            if found_callback:
                found_callback(doc_data, file_path)
        elif not doc_data:
            print(f"Processing and caching {file_path}")
            doc_data = callback_process(file_path)
            self.update_hash_map(file_path, doc_data)
        return doc_data

