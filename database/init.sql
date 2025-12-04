-- BCP Transactions Database Initialization
-- This script creates the initial database structure

-- Create database if not exists (PostgreSQL doesn't support CREATE DATABASE IF NOT EXISTS directly)
-- The database is already created by the POSTGRES_DB environment variable

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    document_number VARCHAR(20) UNIQUE NOT NULL,
    document_type VARCHAR(20) NOT NULL DEFAULT 'DNI',
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    birth_date DATE,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Peru',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    customer_type VARCHAR(20) DEFAULT 'Personal'
);

-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    account_type VARCHAR(20) NOT NULL DEFAULT 'savings',
    currency VARCHAR(3) NOT NULL DEFAULT 'PEN',
    balance DECIMAL(15,2) DEFAULT 0.00,
    available_balance DECIMAL(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color_code VARCHAR(7) DEFAULT '#007bff',
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(account_id) ON DELETE SET NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'PEN',
    description TEXT,
    reference_number VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    merchant_name VARCHAR(255),
    merchant_category VARCHAR(100),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'completed',
    payment_method VARCHAR(50),
    account_number VARCHAR(50),
    destination_account VARCHAR(50),
    fee DECIMAL(15,2) DEFAULT 0.00,
    location VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create transaction_categories junction table
CREATE TABLE IF NOT EXISTS transaction_categories (
    transaction_id INTEGER NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id, category_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_document_number ON users(document_number);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_account_number ON accounts(account_number);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_reference ON transactions(reference_number);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transaction_categories_transaction ON transaction_categories(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_categories_category ON transaction_categories(category_id);

-- Insert default categories
INSERT INTO categories (name, description, color_code, icon) VALUES 
    ('Alimentación', 'Gastos en comida y bebidas', '#28a745', 'fas fa-utensils'),
    ('Transporte', 'Gastos en movilidad y transporte', '#007bff', 'fas fa-car'),
    ('Entretenimiento', 'Gastos en ocio y diversión', '#e83e8c', 'fas fa-gamepad'),
    ('Salud', 'Gastos médicos y farmacia', '#dc3545', 'fas fa-heartbeat'),
    ('Educación', 'Gastos educativos', '#6610f2', 'fas fa-graduation-cap'),
    ('Servicios', 'Servicios públicos y básicos', '#fd7e14', 'fas fa-cogs'),
    ('Compras', 'Compras generales y retail', '#20c997', 'fas fa-shopping-bag'),
    ('Transferencias', 'Transferencias bancarias', '#17a2b8', 'fas fa-exchange-alt'),
    ('Cajero', 'Retiros en cajeros automáticos', '#6c757d', 'fas fa-money-bill-wave'),
    ('Otros', 'Gastos diversos', '#868e96', 'fas fa-ellipsis-h')
ON CONFLICT (name) DO NOTHING;

-- Insert sample user (optional)
INSERT INTO users (document_number, first_name, last_name, email, phone) VALUES 
    ('12345678', 'Usuario', 'Demo', 'demo@bcp.com.pe', '999888777')
ON CONFLICT (document_number) DO NOTHING;

-- Insert sample account (optional)
INSERT INTO accounts (user_id, account_number, account_type, currency, balance, available_balance) VALUES 
    (1, '194-123456789-001', 'savings', 'PEN', 5000.00, 4500.00)
ON CONFLICT (account_number) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (if needed for specific user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;