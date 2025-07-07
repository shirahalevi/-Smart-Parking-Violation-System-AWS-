Smart Parking Violation Management System – AWS Based
------------------------------------------------------------------------------------------------------------------------
Final project for the AWS Cloud Computing course: A cloud-based system for managing and reporting parking violations in a private parking lot.

This project simulates an MVP (Minimum Viable Product) designed for **Mobileye**, demonstrating an end-to-end parking enforcement solution based on AWS services.

------------------------------------------------------------------------------------------------------------------------

🧩 Architecture

The system leverages AWS services for full serverless deployment:

- **AWS Lambda** – handles logic for reporting, alerts, and violation counting
- **Amazon DynamoDB** – stores vehicle data, driver info, and violation history
- **Amazon S3** – stores violation images and static web frontend
- **Amazon SES / SNS** – sends emails and SMS to drivers/managers
- **API Gateway** – exposes REST endpoints
- **IAM** – manages secure access between services

------------------------------------------------------------------------------------------------------------------------

💻 Features

- 🔍 Search for vehicles by license plate
- 🚗 Report new parking violations with reason and image
- 📧 Notify drivers via email (escalating)
- 📱 Alert via SMS to move car
- 📊 Weekly summary to parking manager (no driver names)
- 🛠️ Manage vehicle registry (CRUD)

------------------------------------------------------------------------------------------------------------------------

🌐 Live Interface

A static HTML/CSS/JS interface is hosted on **Amazon S3** and connected live to Lambda APIs.

🔗 **Live Link**:   [http://mobileye-parking-violation.s3-website.eu-north-1.amazonaws.com/index2.html]

------------------------------------------------------------------------------------------------------------------------

📂 Project Structure

```
system_spec/
├── Business Requirement.pdf
├── Architecture Diagram.pdf
└── Presentation.pdf

functions/
├── submit_violation_lambda.py
├── addBulkCar.py
└── ...

interface/
├── index.html
├── style.css
└── script.js
```



------------------------------------------------------------------------------------------------------------------------

👥 Project Team

- Elia Bitan – Project Manager  
- Erel Yogev – System Analyst  
- Shira Fass – Backend Developer  
- Ido Fass – Frontend Developer


