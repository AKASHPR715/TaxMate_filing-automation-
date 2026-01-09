from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth_routes import get_current_user
from app.db.connection import get_sync_db
import logging

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger("admin_api")

@router.delete("/reset", status_code=status.HTTP_200_OK)
async def reset_database(current_user: dict = Depends(get_current_user)):
    """
    ⚠️ DANGER: Completely wipes all data from the database.
    Preserves collections/schemas but removes all documents.
    """
    try:
        db = get_sync_db()
        
        # List of collections to wipe
        collections = [
            "users",
            "form16_part_as",
            "form16_part_bs",
            "ais",
            "itr_filings",
            "token_blacklist"  # Optional: clear blacklist too for a fresh start
        ]
        
        deleted_counts = {}
        
        for col_name in collections:
            result = db[col_name].delete_many({})
            deleted_counts[col_name] = result.deleted_count
            logger.warning(f"Cleared collection {col_name}: {result.deleted_count} documents removed.")
            
        return {
            "message": "Database reset successful. All data has been deleted.",
            "details": deleted_counts
        }
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )
