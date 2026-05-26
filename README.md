# Moein - AI Student Assistance System

Moein is an AI-powered student assistance system designed to help university students manage, understand, and review their academic materials more efficiently. The system combines course and lecture management with AI-based services such as summarization, quiz generation, speech-to-text transcription, notifications, and a retrieval-based chatbot.

## Team Members

- MHD Zaher Krayem
- MHD Yahia Abo Samra
- MHD Awab Kheir
- Othman Darkal

## Project Overview

Moein provides students with a centralized platform for organizing courses and lecture materials. Students can upload lecture files, generate structured summaries, create quizzes from lecture content, transcribe audio lectures, and ask questions through an AI chatbot based on their uploaded academic materials.

The system is built using a microservices architecture to improve scalability, maintainability, and separation of responsibilities between services.

## Main Features

- User registration, login, and account management
- Course creation, editing, deletion, and listing
- Lecture upload and lecture management
- AI-based lecture summarization
- Automatic quiz generation from lecture content
- Speech-to-text transcription for audio lectures
- AI chatbot using Retrieval-Augmented Generation (RAG)
- Notification system for OTP and completed AI tasks
- API Gateway for routing requests between services

## Backend Architecture

The backend is organized into independent microservices. Each service is responsible for a specific part of the system:

- **API Gateway**: Routes frontend requests to the correct backend service.
- **Account & User Service**: Handles authentication, user profiles, and account management.
- **Course & Lecture Service**: Manages courses, lectures, file uploads, and lecture metadata.
- **Summarization Service**: Generates structured summaries from lecture text.
- **Quiz Generator Service**: Creates quizzes and evaluates student answers.
- **Chatbot Service**: Uses RAG to answer questions based on uploaded lecture content.
- **Transcription Service**: Converts audio lectures into text.
- **Notification Service**: Sends OTP codes and AI-task completion notifications.

## Technologies Used

### Backend
- Python
- Django REST Framework
- REST APIs
- JWT Authentication

### Databases
- MySQL
- MongoDB
- Milvus Vector Database

### AI and Processing
- Hugging Face Models
- Qwen Models
- BGE-M3 Embeddings
- Whisper / Faster Whisper
- Retrieval-Augmented Generation (RAG)

### Tools and Infrastructure
- Git
- GitHub
- Docker
- RabbitMQ
- Ngrok

## Purpose of the Repository

This repository contains the backend implementation of the Moein system, including all backend microservices, API routing logic, database integrations, authentication mechanisms, AI-service communication, and asynchronous task processing.

It provides the core server-side logic required to connect the frontend application with AI models, databases, and background processing services.

## Related Repositories

The Moein system is divided into separate repositories to keep backend and frontend development organized and maintainable.

### Frontend Repository

The frontend web application is maintained in a separate GitHub repository:

[Frontend Repository - Moein Senior1 Front-End](https://github.com/Zaher500/Moein-Senior1-Front-End)

This repository contains the React-based user interface of the Moein system, including pages, components, API integration, routing, authentication screens, course and lecture interfaces, chatbot UI, quiz pages, transcription pages, and notification-related frontend features.

### Backend Repository

This repository contains the backend microservices of Moein, including API Gateway routing, account management, course and lecture management, summarization, quiz generation, chatbot service, transcription, notification service, and database integrations.
