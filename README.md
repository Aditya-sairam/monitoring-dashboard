# User Activity Monitoring Tool

This project is a user activity monitoring tool built with Django, Redis, and DynamoDB. It tracks user actions on a web page and provides real-time analytics through a dashboard.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [Usage](#usage)
- [Deployment](#deployment)

## Features

- Track user actions and store them in DynamoDB
- Cache frequently accessed data using Redis
- Display real-time analytics on a dashboard

## Architecture

```plaintext
              +-------------------+
              |    User Browser   |
              +-------------------+
                       |
                       v
              +-------------------+
              |    Django Backend |
              +-------------------+
                       |
     +-----------------+-----------------+
     |                                   |
     v                                   v
+------------+                     +------------+
| Redis Cache|                     |DynamoDB         |
| (Caching)  |                     |(Persistent Storage)|
+------------+                     +----------------+
