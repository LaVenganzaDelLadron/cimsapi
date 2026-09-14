def table_chats():
    return """
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL, 
            userinput TEXT, 
            response TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
            -- Defining the foreign key relationship
            FOREIGN KEY (user_id) REFERENCES users(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )
    """