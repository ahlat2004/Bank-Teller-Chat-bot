-- Seed Data for Bank Teller Chatbot
-- Demo Users, Accounts, Transactions, and Bills

-- Insert Demo Users
INSERT INTO users (name, phone, email) VALUES
('Ali Khan', '03001234567', 'ali.khan@email.com'),
('Sarah Ahmed', '03012345678', 'sarah.ahmed@email.com'),
('Zara Hassan', '03123456789', 'zara.hassan@email.com');

-- Insert Demo Accounts
-- Ali Khan's Accounts
INSERT INTO accounts (user_id, account_no, account_type, balance, currency, status) VALUES
(1, 'PK12ABCD1234567890123456', 'salary', 125450.00, 'PKR', 'active'),
(1, 'PK12ABCD1234567890123457', 'savings', 75300.50, 'PKR', 'active');

-- Sarah Ahmed's Accounts
INSERT INTO accounts (user_id, account_no, account_type, balance, currency, status) VALUES
(2, 'PK98BANK7654321098765432', 'current', 256780.25, 'PKR', 'active'),
(2, 'PK98BANK7654321098765433', 'savings', 189500.00, 'PKR', 'active');

-- Zara Hassan's Accounts
INSERT INTO accounts (user_id, account_no, account_type, balance, currency, status) VALUES
(3, 'PK45CITY4567890123456789', 'salary', 95600.00, 'PKR', 'active'),
(3, 'PK45CITY4567890123456790', 'savings', 45250.75, 'PKR', 'active');

-- Insert Sample Transactions (Ali Khan - Account 1)
INSERT INTO transactions (account_id, type, amount, payee, description, balance_after, timestamp) VALUES
(1, 'credit', 120000.00, 'Employer', 'Monthly Salary', 120000.00, datetime('now', '-25 days')),
(1, 'debit', 5000.00, 'ATM Withdrawal', 'Cash withdrawal', 115000.00, datetime('now', '-20 days')),
(1, 'transfer_out', 15000.00, 'Sarah Ahmed', 'Transfer to friend', 100000.00, datetime('now', '-18 days')),
(1, 'debit', 3500.00, 'Electricity Bill', 'LESCO payment', 96500.00, datetime('now', '-15 days')),
(1, 'credit', 25000.00, 'Freelance Income', 'Project payment', 121500.00, datetime('now', '-10 days')),
(1, 'debit', 8000.00, 'Shopping', 'Online purchase', 113500.00, datetime('now', '-7 days')),
(1, 'transfer_out', 10000.00, 'Zara Hassan', 'Gift', 103500.00, datetime('now', '-5 days')),
(1, 'debit', 2500.00, 'Mobile Bill', 'Jazz prepaid', 101000.00, datetime('now', '-3 days')),
(1, 'credit', 30000.00, 'Client Payment', 'Consulting fee', 131000.00, datetime('now', '-2 days')),
(1, 'debit', 5550.00, 'Grocery', 'Metro cash & carry', 125450.00, datetime('now', '-1 day'));

-- Insert Sample Transactions (Sarah Ahmed - Account 3)
INSERT INTO transactions (account_id, type, amount, payee, description, balance_after, timestamp) VALUES
(3, 'credit', 250000.00, 'Business Revenue', 'Monthly income', 250000.00, datetime('now', '-28 days')),
(3, 'debit', 45000.00, 'Rent Payment', 'Office rent', 205000.00, datetime('now', '-26 days')),
(3, 'transfer_in', 15000.00, 'Ali Khan', 'Payment received', 220000.00, datetime('now', '-18 days')),
(3, 'debit', 12500.00, 'Utilities', 'Various bills', 207500.00, datetime('now', '-12 days')),
(3, 'credit', 65000.00, 'Invoice Payment', 'Client XYZ', 272500.00, datetime('now', '-8 days')),
(3, 'debit', 15720.00, 'Staff Salaries', 'Employee payments', 256780.00, datetime('now', '-2 days'));

-- Insert Sample Transactions (Zara Hassan - Account 5)
INSERT INTO transactions (account_id, type, amount, payee, description, balance_after, timestamp) VALUES
(5, 'credit', 95000.00, 'Salary', 'Monthly salary', 95000.00, datetime('now', '-25 days')),
(5, 'transfer_in', 10000.00, 'Ali Khan', 'Gift received', 105000.00, datetime('now', '-5 days')),
(5, 'debit', 8000.00, 'Shopping', 'Clothes', 97000.00, datetime('now', '-4 days')),
(5, 'debit', 1400.00, 'Internet Bill', 'StormFiber', 95600.00, datetime('now', '-1 day'));

-- Insert Pending Bills (Ali Khan)
INSERT INTO bills (user_id, type, amount, due_date, status, reference_no) VALUES
(1, 'electricity', 4200.00, date('now', '+5 days'), 'unpaid', 'LESCO-2024-001'),
(1, 'mobile', 1800.00, date('now', '+8 days'), 'unpaid', 'JAZZ-2024-045'),
(1, 'gas', 2500.00, date('now', '+10 days'), 'unpaid', 'SSGC-2024-078');

-- Insert Pending Bills (Sarah Ahmed)
INSERT INTO bills (user_id, type, amount, due_date, status, reference_no) VALUES
(2, 'internet', 3500.00, date('now', '+3 days'), 'unpaid', 'PTCL-2024-234'),
(2, 'electricity', 8900.00, date('now', '+7 days'), 'unpaid', 'KESC-2024-567');

-- Insert Pending Bills (Zara Hassan)
INSERT INTO bills (user_id, type, amount, due_date, status, reference_no) VALUES
(3, 'mobile', 1500.00, date('now', '+6 days'), 'unpaid', 'TELENOR-2024-890'),
(3, 'water', 800.00, date('now', '+12 days'), 'unpaid', 'KWSB-2024-112');

-- Insert Demo Cards (Ali Khan)
INSERT INTO cards (account_id, card_number, card_type, card_name, expiry_date, cvv, status, credit_limit) VALUES
(1, '4532123456789012', 'debit', 'Ali Khan', date('now', '+730 days'), '123', 'active', 0),
(1, '5412987654321098', 'credit', 'Ali Khan', date('now', '+1095 days'), '456', 'active', 150000.00);

-- Insert Demo Cards (Sarah Ahmed)
INSERT INTO cards (account_id, card_number, card_type, card_name, expiry_date, cvv, status, credit_limit) VALUES
(3, '4916234567890123', 'debit', 'Sarah Ahmed', date('now', '+900 days'), '789', 'active', 0),
(3, '5523456789012345', 'credit', 'Sarah Ahmed', date('now', '+1200 days'), '321', 'active', 300000.00);

-- Insert Demo Cards (Zara Hassan)
INSERT INTO cards (account_id, card_number, card_type, card_name, expiry_date, cvv, status, credit_limit) VALUES
(5, '4024123456789876', 'debit', 'Zara Hassan', date('now', '+800 days'), '654', 'active', 0);