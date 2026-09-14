def table_investigation_notes():
    return """
        CREATE TABLE IF NOT EXISTS investigation_notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            incident_id INT NOT NULL, 
            analyst_id INT NOT NULL, 
            note TEXT, 
            recommendation TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
            
            -- Defining the foreign key relationship
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )
    """