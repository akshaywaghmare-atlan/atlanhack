# Frontend Documentation

## Overview

This frontend project is built using Nuxt.js and leverages a custom Application UI SDK to create dynamic and responsive user interfaces. The project includes various components and pages that interact with backend APIs to fetch and display data.

## Table of Contents

1. [Installation](#installation)
2. [Project Structure](#project-structure)
5. [Usage](#usage)
6. [API Integration](#api-integration)
7. [Styling](#styling)

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/your-repo/frontend.git
    ```

2. Navigate to the project directory:
    ```sh
    cd frontend
    ```

3. Install the dependencies:
    ```sh
    npm install
    ```

4. Start the development server:
    ```sh
    npm run dev
    ```

5. Generate static files:
    ```sh
    npm run generate
    ```

## Project Structure

The project structure is organized as follows:

- `assets/`: Contains static assets like images, fonts, and other media files.
- `components/`: Reusable Vue components that can be used across different pages.
- `pages/`: Contains the main pages of the application. Each `.vue` file in this directory represents a different route in the application. The pages folder works with Vue Router to map each file to a specific route. For example, `index.vue` maps to the root route `/`, and `telemetry.vue` maps to the `/telemetry` route.
- `styles/`: Global styles and CSS files.
- `api/`: API service files for making HTTP requests to the backend.

## Usage

1. Install the dependencies:
    ```sh
    npm install
    ```

2. Start the development server:
    ```sh
    npm run dev
    ```

## API Integration
To make an API call using `apiClient.ts`, follow these steps:

1. Declare your API endpoints in `api/index.ts`:
    ```javascript
    export const urls = {
        telemetry: {
            logs: '/telemetry/logs',
            events: '/telemetry/events',
        },
    };
    ```
2. Use the `apiClient` to make an API call. For example, to fetch telemetry logs:
    ```javascript
    const fetchTelemetryLogs = async () => {
        try {
            const response = await apiClient.get(urls.telemetry.logs);
            if (response && response.data) {
                return response.data;
            } else {
                return [];
            }
        } catch (error) {
            console.error('Error fetching telemetry logs:', error);
            return [];
        }
    };
    ```

