# Postman Testing Guide

This guide explains how to test the To-Do API using Postman, including running automated test collections and seeding data to test pagination.

## 1. Importing and Running the Collection
You can run the entire test suite using the Postman Collection Runner.

1. **Import the JSON Collection**: 
   - Open Postman.
   - Click the **Import** button.
   - Select and upload the `TodoAPI_Postman_Collection.json` file from the root directory.
2. **Run the Collection**:
   - Click on the imported collection `To-Do API (Django REST)`.
   - Click the **Run** button to open the Collection Runner.
   - Ensure the order of execution is correct (Authentication first, followed by Creation, Pagination, then Deletion).
   - Click **Run To-Do API** to execute the tests. All test assertions (e.g. 200 OK, 201 Created) should pass.

## 2. Testing Pagination, Filtering, and Ordering
To effectively test the pagination and filtering endpoints, you need a large dataset. Instead of manually creating tasks, you can use the provided database seeder.

1. **Run the Seeder Script**:
   In your terminal, run the following command to populate the database with over 50 tasks from `tasks_data.json`:
   ```bash
   python seed_db.py
   ```
   *Note: This script automatically creates a user named `testuser` with the password `Password123!` who owns all the seeded tasks.*

2. **Update Username in Postman**:
   - In Postman, open the **Login (Success)** request under the `1. Authentication` folder.
   - Ensure the request body uses the seeder's credentials:
     ```json
     {
         "username": "testuser",
         "password": "Password123!"
     }
     ```
   - Send the Login request to automatically save the new `access_token` into your collection variables.

3. **Test Pagination**:
   - Navigate to the `3. Pagination and Filtering` folder in Postman.
   - Run the **List Tasks** requests (e.g., `Page 1, Limit 2`, `Filter Status Pending`, `Sort Created At Asc`).
   - You should now see the robust, 50+ item dataset being paginated, filtered, and ordered correctly!
