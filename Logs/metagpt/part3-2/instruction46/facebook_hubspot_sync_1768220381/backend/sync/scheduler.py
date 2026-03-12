import os
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from threading import Lock

from backend.sync.mapping import run_mapping_sync
from backend.utils.logger import get_logger
from backend.utils.notifier import notify_error, notify_success

# Configurable sync interval (seconds)
DEFAULT_SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", 3600))  # Default: 1 hour

logger = get_logger(__name__)

# Scheduler instance and lock for thread safety
scheduler = BackgroundScheduler()
interval_lock = Lock()
current_interval = DEFAULT_SYNC_INTERVAL

def sync_job():
    """
    The main sync job: fetch Facebook ad metrics, map to HubSpot contacts/deals, update HubSpot.
    Logs and notifies on success/failure.
    """
    logger.info(f"[{datetime.utcnow()}] Starting scheduled Facebook-HubSpot sync job.")
    try:
        result = run_mapping_sync()
        logger.info(f"Sync job completed successfully: {result}")
        notify_success("Facebook-HubSpot sync completed successfully.")
    except Exception as e:
        error_msg = f"Sync job failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        notify_error(error_msg)

def scheduler_start():
    """
    Start the scheduler and add the sync job.
    """
    with interval_lock:
        if not scheduler.running:
            scheduler.add_job(sync_job, 'interval', seconds=current_interval, id='facebook_hubspot_sync', replace_existing=True)
            scheduler.start()
            logger.info(f"Scheduler started with interval {current_interval} seconds.")

def run_sync():
    """
    Manually trigger the sync job.
    """
    logger.info("Manual sync triggered.")
    sync_job()

def adjust_interval(new_interval: int):
    """
    Adjust the sync interval for the scheduled job.
    """
    global current_interval
    with interval_lock:
        current_interval = new_interval
        if scheduler.get_job('facebook_hubspot_sync'):
            scheduler.reschedule_job('facebook_hubspot_sync', trigger='interval', seconds=current_interval)
            logger.info(f"Sync interval adjusted to {current_interval} seconds.")
        else:
            scheduler.add_job(sync_job, 'interval', seconds=current_interval, id='facebook_hubspot_sync', replace_existing=True)
            logger.info(f"Sync job added with interval {current_interval} seconds.")

def get_sync_status():
    """
    Get the current status of the scheduler and sync job.
    """
    job = scheduler.get_job('facebook_hubspot_sync')
    status = {
        "running": scheduler.running,
        "interval_seconds": current_interval,
        "next_run_time": job.next_run_time.isoformat() if job and job.next_run_time else None
    }
    return status