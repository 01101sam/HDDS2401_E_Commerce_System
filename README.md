# e-Commerce API Backend

# Description

This is a simple e-Commerce API backend that provides endpoints for managing products, orders, and users. It is built
using Python and the FastAPI framework, with asynchronous operations for high performance.

# Develop Approach

The software is developed using the following approach:

1. **Programming Language**: Python
    - **Reason**: Python is a versatile and widely-used language, especially suitable for web development and data
      manipulation. It has a rich ecosystem of libraries and frameworks that facilitate rapid development.

2. **Framework**: FastAPI
    - **Reason**: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based
      on
      standard Python type hints. It provides automatic validation, serialization, and documentation of API endpoints,
      making development efficient and maintainable.

4. **ORM**: Odmantic based on Pydantic
    - **Reason**: Odmantic is a modern, fast, and asynchronous ODM (Object-Document Mapper) for MongoDB with Pydantic
      models. It allows for seamless integration of MongoDB with FastAPI, providing a clean and efficient way to work
      with MongoDB databases.

5. **Cloud Service Model**: Platform as a Service (PaaS)
    - **Reason**: PaaS provides a platform allowing customers to develop, run, and manage applications without the
      complexity of building and maintaining the infrastructure. It is cost-effective, scalable, and easy to deploy and
      manage.

6. **Database**: MongoDB
    - **Reason**: MongoDB is a popular NoSQL database that provides flexibility, scalability, and performance for
      applications. It is well-suited for document-based data storage and retrieval, making it ideal for e-commerce
      applications.

# Features

> Note: CURD stands for Create, Update, Read, Delete

The e-commerce API backend provides the following features:

- [x] Authentication
    - [x] Register
    - [x] Login
    - [x] Reset Password (via Email)

- [x] Products
    - [x] CURD (Admin)
    - [x] Get Product by ID
    - [x] List All Products
    - [x] List Products by Category
    - [x] Change Product Status (Admin)

- [x] Cart
    - [x] CURD (Admin)

- [x] Orders
    - [x] Create Order
    - [x] Update Order Status (Admin)
    - [x] Get Order by ID
    - [x] List All Orders (Customer can list their own / Admin can fetch all)
    - [x] Cancel Order (Admin)
    - [x] Refund Payment (Admin)

- [x] Users
    - [x] Change Name, Password, Email
    -  [x] Change Role (Admin)
    - [x] List All Users (Admin)
    - [x] Get User by ID (Admin)
    - [x] Delete User (Admin)

- [x] Address (With Phone Number)
    - [x] CURD

- [x] Categories
    - [x] CURD (Admin)

- [x] Checkout
    - [x] Summary
    - [x] Get Payment Methods
    - [x] Place Order
    - [x] Callback of Payment Gateway

- [x] Media
    - [x] Upload Image (Admin)
    - [x] Download Image

- [x] Shipping
    - [x] Change Shipping Carrier / Status (Admin)
    - [x] Get Shipping Status (With Optional Tracking Number)

- [x] Review
    - [x] Create Review
    - [x] Delete Review (Admin)
    - [x] List Reviews by Product (Admin)

# Deployment

## Prerequisites

- Azure Account

To install and run the e-Commerce system, follow documentation in the `docs` folder.
