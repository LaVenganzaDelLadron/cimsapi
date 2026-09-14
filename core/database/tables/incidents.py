def table_incidents():
    return """
        CREATE TABLE IF NOT EXISTS incidents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            category_id INT NOT NULL,
            title VARCHAR(255),
            description TEXT,
            severity ENUM('low','medium','high','critical'),
            status ENUM('new','investigating','resolved','closed'),
            location VARCHAR(255),
            incident_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_to INT NULL,
            resolve_at DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
            -- Defining the foreign key relationship
            FOREIGN KEY (user_id) REFERENCES users(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        
            FOREIGN KEY (assigned_to) REFERENCES users(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )
    """