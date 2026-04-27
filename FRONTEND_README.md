# Expense Tracking System - Complete Project

A modern, full-stack expense tracking application with a Python FastAPI backend and React TypeScript frontend.

## Project Structure

```
expense-tracking-system/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # API client and utilities
│   │   ├── store/        # State management
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── README.md
├── src/                  # Python backend
│   ├── api/             # API routes
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   └── config/          # Configuration
├── tests/               # Backend tests
├── setup-frontend.sh    # Frontend setup script
└── README.md           # This file
```

## Features

### Backend (FastAPI + PostgreSQL)
- ✅ User authentication with JWT
- ✅ Transaction management (CRUD)
- ✅ Category management (income/expense)
- ✅ Source management (bank accounts, cards)
- ✅ Budget tracking
- ✅ RESTful API with OpenAPI documentation
- ✅ Database migrations with Alembic
- ✅ Comprehensive test coverage

### Frontend (React + TypeScript)
- ✅ Modern, professional UI design
- ✅ User authentication flow
- ✅ Dashboard with analytics
- ✅ Transaction management with filters
- ✅ Category & source management
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Real-time form validation
- ✅ Toast notifications & confirmations
- ✅ Empty states & loading skeletons

## Quick Start

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database (PostgreSQL)
# Update .env with your database URL

# Run migrations
alembic upgrade head

# Start backend server
uvicorn src.main:app --reload
```

Backend will run on **http://localhost:8000**

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on **http://localhost:3000**

### 3. Access the Application

1. Open browser to **http://localhost:3000**
2. Register a new account
3. Start tracking your expenses!

## Documentation

- **Frontend Setup Guide**: [`frontend/SETUP_GUIDE.md`](frontend/SETUP_GUIDE.md)
- **Frontend README**: [`frontend/README.md`](frontend/README.md)
- **API Documentation**: [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)
- **Backend Quick Start**: [`QUICK_START.md`](QUICK_START.md)
- **Deployment Guide**: [`DEPLOYMENT.md`](DEPLOYMENT.md)

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Testing**: Pytest

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Routing**: React Router
- **HTTP Client**: Axios
- **Icons**: Lucide React

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Transactions
- `GET /api/v1/transactions` - List transactions (with filters)
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/{id}` - Get transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction

### Categories
- `GET /api/v1/categories` - List categories
- `POST /api/v1/categories` - Create category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Sources
- `GET /api/v1/sources` - List sources
- `POST /api/v1/sources` - Create source
- `PUT /api/v1/sources/{id}` - Update source
- `DELETE /api/v1/sources/{id}` - Delete source

### Budgets
- `GET /api/v1/budgets` - List budgets
- `POST /api/v1/budgets` - Create budget
- `PUT /api/v1/budgets/{id}` - Update budget
- `DELETE /api/v1/budgets/{id}` - Delete budget

Full API documentation available at **http://localhost:8000/docs** (Swagger UI)

## Development

### Backend Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run with hot reload
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

```bash
cd frontend

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost/expense_tracker
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Frontend
API proxy configured in `vite.config.ts` to forward `/api` requests to `http://localhost:8000`

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend
Currently manual testing. Future: Jest + React Testing Library

## Deployment

### Backend Deployment
- Docker support included
- Deploy to cloud platforms (AWS, GCP, Azure, Heroku)
- See [`DEPLOYMENT.md`](DEPLOYMENT.md) for details

### Frontend Deployment
- Build static files: `npm run build`
- Deploy to Vercel, Netlify, S3, or any static host
- Or serve with Nginx/Apache

## Design Principles

The frontend follows professional design guidelines:

- **Tool-grade, not template-grade**: Information-dense, scannable interface
- **White canvas**: Clean background with purposeful color usage
- **Consistent spacing**: 4px base unit with 8-point grid
- **Typography**: Inter font with clear hierarchy
- **Accessible**: WCAG AA compliant, keyboard navigation, screen reader support

## Project Status

✅ **Completed Features**:
- User authentication & authorization
- Transaction CRUD operations
- Category management
- Source management
- Dashboard with analytics
- Responsive design
- API documentation

🚧 **Future Enhancements**:
- Budget tracking UI
- CSV/Excel import
- Recurring transactions
- Multi-currency support
- Charts & visualizations
- Mobile app (React Native)
- Email notifications

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check documentation in respective folders
- Review API documentation at `/docs`
- Check browser console for frontend errors
- Check backend logs for API errors

---

**Built with Python, FastAPI, React, and TypeScript** 🚀
