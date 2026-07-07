import sqlite3
import os
from typing import Tuple, Optional
from helpers.log_loader import logger
from .base import BaseSpeedtestClient

class SQLiteClient(BaseSpeedtestClient):
    def get_latest_result(self) -> Tuple[Optional[float], Optional[float]]:
        db_path = self.config.database_path
        if not db_path:
            logger.error("<sqlite_speedtest> database_path is missing in config.")
            return None, None

        if not os.path.exists(db_path):
            logger.error(f"<sqlite_speedtest> Database file does not exist: {db_path}")
            return None, None

        query = self.config.query or "SELECT dl, ul FROM speedtest_users ORDER BY id DESC LIMIT 1"
        dl_col = self.config.download_column or "dl"
        ul_col = self.config.upload_column or "ul"
        unit = self.config.speed_unit or "Mbit"

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            if not row:
                logger.debug("<sqlite_speedtest> No records found in speedtest table.")
                return None, None
            
            # Retrieve by column name or fallback to index 0 and 1
            try:
                dl = row[dl_col]
                ul = row[ul_col]
            except IndexError:
                # If row does not support keys, fallback to index
                dl = row[0]
                ul = row[1]
                
            if dl is None or ul is None:
                return None, None
                
            # Convert values to float
            dl_val = float(dl)
            ul_val = float(ul)
            
            # Convert from the database unit to bits/sec
            from helpers.bit_convert import bit_conv
            download_bits = bit_conv(dl_val, unit, 'bit')
            upload_bits = bit_conv(ul_val, unit, 'bit')
            
            return download_bits, upload_bits
        except Exception as e:
            logger.error(f"<sqlite_speedtest> SQLite error querying speedtest results: {e}")
            return None, None
        finally:
            if conn:
                conn.close()
