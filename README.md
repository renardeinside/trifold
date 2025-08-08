# 🔷 Trifold

A full-stack real-time table editor built with FastAPI, React, Databricks Apps and Lakebase.

## 🏗 Architecture Overview

The application consists of two main parts:
- Frontend: React + Vite application with TanStack Router
- Backend: FastAPI application serving both the frontend and API endpoints

### ✨ Key Features
- Modern React frontend with TanStack Router for routing
- FastAPI backend with automatic OpenAPI client generation
- Databricks SDK integration
- Component-based architecture with loading states
- Dark mode support
- Type-safe API communication

## 🛠 Technology Stack

### 🎨 Frontend
- React + Vite
- TanStack Router for routing
- TypeScript for type safety
- Tailwind CSS for styling
- Shadcn/ui components
- Orval for API client generation

### ⚡ Backend
- FastAPI for API development
- Uvicorn for ASGI server
- sqlmodel for database operations
- Databricks SDK for Databricks integration

## 💻 Development Setup

### 📋 Prerequisites
- Python 3.11+
- Node.js 20+
- Yarn package manager
- UV package manager for Python

### 🚀 Installation

1. Install Python dependencies:
```bash
uv sync --all-packages
```

2. Install frontend dependencies:
```bash
yarn --cwd src/trifold/ui install
```

### 🔧 Development Commands

#### 🌐 Frontend
```bash
# Start development server
yarn --cwd src/trifold/ui dev

# Generate API client
yarn --cwd src/trifold/ui orval
```

#### 🖥 Backend
```bash
# Start development server
uvicorn trifold.app.app:app --reload
```

To populate the database with some data, run:
```bash
python ops/populate_db.py
```

For load testing, run:
```bash
DATABRICKS_CONFIG_PROFILE=<your-profile> locust -f ops/locust_test.py --host=<your-app-url>
```

#### 📦 Deployment

1. Create a new Lakebase instance:
```
databricks database create-database-instance --capacity CU_1 trifold -p <your-profile>
```

2. Deploy the app to Databricks:
```
databricks bundle deploy -p <your-profile>
```

3. Grant the app service principal access to the Lakebase instance in the Databricks UI.
4. Start the app:
```
databricks bundle run trifold -p <your-profile>
```

## 📁 Project Structure

```
src/trifold/
├── app/                    # Backend application
│   ├── api.py             # API routes
│   ├── app.py             # Main application
│   ├── models.py          # Database models
│   └── utils.py           # Utilities
└── ui/                    # Frontend application
    ├── src/
    │   ├── components/    # React components
    │   ├── routes/        # Application routes
    │   ├── lib/           # Utilities and API client
    │   └── main.tsx       # Application entry
    └── package.json       # Frontend dependencies
```

## 🔄 Development Patterns

### 📊 Model Convention
Each entity follows a three-model pattern:
- `EntityName` - Database entity structure
- `EntityNameIn` - Creation/form input structure
- `EntityNameView` - API response structure

### 🧩 Component Architecture
Components follow a consistent pattern:
1. Static elements render immediately
2. API data is fetched using `useXSuspense` hooks
3. Loading states use `Skeleton` components
4. Data renders once fetched

### 🔌 API Integration
- All API routes have defined response models
- Frontend uses auto-generated type-safe clients
- Background tasks handle asynchronous operations

## 📝 Best Practices

- Use `useXSuspense` hooks for data fetching
- Implement loading states with Suspense and Skeleton components
- Create reusable components
- Follow consistent naming conventions
- Ensure proper error handling
- Use type-safe data access patterns


## Sources

Project icon is from taken from [svgrepo.com](https://www.svgrepo.com/svg/17314/triangle) and slightly modified, original icon is CC0 licensed.