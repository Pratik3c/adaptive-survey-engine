import sqlite3

DB_PATH = "data/survey.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        UPDATE survey_sessions
        SET status = ?
        WHERE id = ? AND project_id = ? AND status = ?
    """, ("completed", 2, 1, "active"))

    conn.commit()

    if cursor.rowcount == 1:
        print("Successfully updated session status to 'completed'.")
    elif cursor.rowcount == 0:
        print("No matching active session found.")
    else:
        print(f"Updated {cursor.rowcount} rows.")

    # Verify the result
    cursor.execute("""
        SELECT id, project_id, status
        FROM survey_sessions
        WHERE id = ? AND project_id = ?
    """, (2, 1))

    print("Current record:", cursor.fetchone())

except sqlite3.Error as e:
    conn.rollback()
    print(f"Database error: {e}")

finally:
    conn.close()