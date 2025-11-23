---
globs: |-
  **/*.py
  **/*.html
  **/*.js
  **/*.css
description: Summary of the tracking and invoicing application structure and functionality
alwaysApply: true
---

This application is a web-based tracking and invoicing system built with Flask. It includes:
1. A tracking system that allows users to track shipments by entering a tracking number
2. A timeline visualization of shipment status
3. A PDF invoice generation system with customizable fields
4. A simple authentication system
The application uses Flask for the web framework, SQLite for the database, ReportLab for PDF generation, and PyPDF2 for PDF manipulation.

Tracking System:
Allows users to track shipments by entering a tracking number.
Displays the current status of a shipment in a timeline format.
Provides a management interface for viewing all tracking data.
Invoicing System:
Generates PDF invoices based on user input.
Allows users to upload files and input various details for invoice generation.
Authentication:
Simple password-based login system.