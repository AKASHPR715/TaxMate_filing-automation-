import logging
from typing import Optional
# Attempt to import ExtractRun to locate the File model
try:
    from llama_cloud.types import ExtractRun
except ImportError:
    ExtractRun = None

logger = logging.getLogger("llama_patch")

def apply_llama_cloud_patch():
    """
    Patches llama_cloud models to handle API discrepancies,
    specifically allowing None for external_file_id.
    """
    if not ExtractRun:
        logger.warning("⚠️ Could not import llama_cloud.types.ExtractRun. Patch skipped.")
        return

    try:
        # Resolve the File model from ExtractRun
        FileModel = None
        
        # Try finding the field in V1 style (confirmed usage in testing)
        if hasattr(ExtractRun, '__fields__'):
             FileModel = ExtractRun.__fields__['file'].type_
        elif hasattr(ExtractRun, 'model_fields'): # Fallback for V2
             FileModel = ExtractRun.model_fields['file'].annotation

        if FileModel:
            # Patch Pydantic V1
            if hasattr(FileModel, '__fields__'):
                field = FileModel.__fields__.get('external_file_id')
                if field:
                    field.required = False
                    field.allow_none = True
                    # We leave type_ mostly alone to avoid breaking internal logic, 
                    # but allow_none=True is key.
                    logger.info("✅ Patched llama_cloud.types.File.external_file_id to allow None (V1)")
                    print("✅ LlamaCloud Patch Applied: external_file_id is now optional.")
                    return True
            
            # Patch Pydantic V2 (fallback)
            if hasattr(FileModel, 'model_fields'):
                 field_info = FileModel.model_fields.get('external_file_id')
                 if field_info:
                      import pydantic
                      from typing import Optional
                      # In V2, we might need to be more aggressive
                      field_info.annotation = Optional[str]
                      field_info.required = False
                      field_info.default = None
                      logger.info("✅ Patched llama_cloud.types.File.external_file_id to allow None (V2)")
                      print("✅ LlamaCloud Patch Applied: external_file_id is now optional (V2).")
                      return True

    except Exception as e:
        logger.error(f"❌ Failed to patch llama_cloud: {e}")
    
    return False
