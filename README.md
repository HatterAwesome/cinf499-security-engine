# CINF 499 — Security Engine

**Stetson University | Senior Research Project**

## Project Overview

This project explores the use of artificial intelligence to analyze architectural floor plans and support physical access control system planning.

The project includes an access control management dashboard and an experimental Pix2Pix image-to-image translation model.

## Project Components

### Access Control Dashboard

A Java Spring Boot application featuring:

- User authentication and role-based access control
- Door management
- User administration
- Access event tracking
- Document uploads

**Technologies:** Java, Spring Boot, Spring Security, Thymeleaf, and MongoDB.

See [Frontend Documentation](frontend/README.md).

### Pix2Pix — Floor Plan Analysis

An experimental machine learning component focused on architectural floor plan processing.

Current work includes:

- Floor plan dataset preparation
- Room label processing
- Paired training image generation
- Pix2Pix model training and testing
- Dataset validation

**Technologies:** Python, PyTorch, and Pix2Pix.

### Backend

The repository includes a backend directory. Integration between the access control dashboard and the Pix2Pix model is planned for future development.

## Repository Structure

    cinf499-security-engine/
    ├── backend/
    ├── frontend/
    ├── pix2pix/
    │   ├── preprocessing/
    │   └── evaluation/
    ├── README.md
    └── .gitignore

## Current Status

The Access Control Dashboard has been added to the main repository. Pix2Pix dataset preparation, model training, and evaluation are ongoing.

The dashboard and Pix2Pix model are currently separate components.

## Academic Information

**Course:** CINF 499 — Senior Research

**Institution:** Stetson University

**Focus:** Artificial Intelligence and Physical Access Control Systems
