# Fin_Flow
# Django Finance Project

## Overview
This is a Django-based finance project where users can register, log in, send and receive money, perform various transactions, and have top-up and daily transaction limits. The system includes an admin dashboard with full control over user accounts, wallets, transactions, and fraud detection.

---

## Features
### **1. User Management**
- `POST /api/register/` → User registration  
- `POST /api/login/` → User login (JWT or Django auth)  
- `GET /api/user/profile/` → Get user profile  
- `PUT /api/user/profile/update/` → Update user profile  
- `POST /api/user/change-password/` → Change password  
- `POST /api/user/reset-password/` → Reset password  
- `POST /api/user/verify-kyc/` → Upload and verify KYC (e.g., ID verification)  
- `POST /api/user/logout/` → Logout user  


### **2. Wallet Management**
- `GET /api/wallet/` → Get user wallet details  
- `POST /api/wallet/top-up/` → Fund wallet (via bank/card)  
- `POST /api/wallet/withdraw/` → Withdraw money from wallet  
- `GET /api/wallet/transactions/` → View wallet transactions  
- `POST /api/wallet/set-transaction-limit/` → Set daily transaction limit  
- `POST /api/wallet/set-topup-limit/` → Set wallet funding limit  

### **3. Transaction System**
- `POST /api/transactions/send-money/` → Send money to another user  
- `POST /api/transactions/receive-money/` → Receive money (if manual confirmation is needed)  
- `GET /api/transactions/history/` → Get all transactions  
- `GET /api/transactions/<transaction_id>/` → Get specific transaction details  
- `POST /api/transactions/cancel/` → Cancel a pending transaction  
- `POST /api/transactions/refund/` → Request a refund  

### **4. Payment Integrations**
- `POST /api/payments/process/` → Process payment via card/bank  
- `GET /api/payments/status/` → Check payment status  
- `POST /api/payments/webhook/` → Payment gateway webhook listener  

### **5. Security & Fraud Prevention**
- `POST /api/security/enable-2fa/` → Enable two-factor authentication  
- `POST /api/security/disable-2fa/` → Disable two-factor authentication  
- `POST /api/security/verify-otp/` → Verify OTP for transactions  
- `GET /api/security/transaction-limits/` → Get user’s transaction limits  
- `POST /api/security/report-fraud/` → Report fraudulent activity  

---

## **Admin Dashboard**

### **1. User Management**
- `GET /api/admin/users/` → Get all users  
- `GET /api/admin/users/<user_id>/` → Get details of a specific user  
- `POST /api/admin/users/block/` → Block a user from performing transactions  
- `POST /api/admin/users/unblock/` → Unblock a previously blocked user  
- `POST /api/admin/users/delete/` → Delete a user account  
- `POST /api/admin/users/reset-password/` → Force-reset user password  
- `POST /api/admin/users/update-role/` → Assign user roles (e.g., Admin, Support, User)  

### **2. Wallet & Transaction Management**
- `GET /api/admin/wallets/` → Get all user wallets and balances  
- `GET /api/admin/wallets/<user_id>/` → Get a specific user's wallet details  
- `POST /api/admin/wallets/freeze/` → Freeze a user’s wallet  
- `POST /api/admin/wallets/unfreeze/` → Unfreeze a user’s wallet  
- `GET /api/admin/transactions/` → View all transactions  
- `GET /api/admin/transactions/<transaction_id>/` → Get details of a specific transaction  
- `POST /api/admin/transactions/reverse/` → Reverse a transaction  
- `POST /api/admin/transactions/flag/` → Flag a suspicious transaction  
- `POST /api/admin/transactions/delete/` → Delete a fraudulent transaction  

### **3. KYC (Know Your Customer) Management**
- `GET /api/admin/kyc/pending/` → View all pending KYC requests  
- `GET /api/admin/kyc/<user_id>/` → Get a specific user's KYC details  
- `POST /api/admin/kyc/approve/` → Approve a user’s KYC verification  
- `POST /api/admin/kyc/reject/` → Reject a user’s KYC with reasons  

### **4. Limits & Restrictions**
- `GET /api/admin/limits/` → View all user transaction limits  
- `GET /api/admin/limits/<user_id>/` → View a specific user’s limits  
- `POST /api/admin/limits/update/` → Update a user’s daily transaction limit  
- `POST /api/admin/limits/reset/` → Reset a user’s limits  

### **5. Fraud Detection & Security**
- `GET /api/admin/fraud-reports/` → View all fraud reports  
- `POST /api/admin/fraud/investigate/` → Mark a report as "Under Investigation"  
- `POST /api/admin/fraud/resolve/` → Resolve a fraud case  
- `POST /api/admin/fraud/block-user/` → Block a user involved in fraudulent activities  
- `POST /api/admin/fraud/report-to-authorities/` → Report fraud to legal authorities  

### **6. System Monitoring & Logs**
- `GET /api/admin/system-logs/` → View system activity logs  
- `GET /api/admin/logs/<user_id>/` → View logs for a specific user  
- `POST /api/admin/logs/clear/` → Clear old system logs  
- `GET /api/admin/analytics/transactions/` → Get transaction trends & insights  
- `GET /api/admin/analytics/users/` → Get user activity statistics  

### **7. Notifications & Alerts**
- `POST /api/admin/notifications/send/` → Send notifications to all users  
- `POST /api/admin/notifications/send/<user_id>/` → Send a direct notification to a user  
- `GET /api/admin/notifications/logs/` → View all sent notifications  

---

