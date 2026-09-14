def table_attachments():
    return """
       CREATE TABLE IF NOT EXISTS attachments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            incident_id INT NOT NULL, 
            filename VARCHAR(255), 
            filepath VARCHAR(255), 
            filetype VARCHAR(255), 
            uploaded_by INT NOT NULL, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
            -- Defining the foreign key relationship
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )
    """