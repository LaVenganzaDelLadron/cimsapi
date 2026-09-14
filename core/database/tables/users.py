def table_user():
    return """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            firstname VARCHAR(255), 
            lastname VARCHAR(255), 
            username VARCHAR(255), 
            email VARCHAR(255) UNIQUE, 
            password VARCHAR(255), 
            role ENUM('admin', 'analyst', 'user'), 
            status ENUM('active', 'inactive', 'pending'),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """