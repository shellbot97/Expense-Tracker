# Expense Tracker Frontend

Modern, responsive frontend for the Expense Tracking System built with React, TypeScript, and Tailwind CSS.

## Features

- **User Authentication**: Secure login and registration
- **Dashboard**: Overview of income, expenses, and spending by category
- **Transaction Management**: Add, edit, delete, and filter transactions
- **Categories**: Organize transactions into custom categories
- **Sources**: Manage financial sources (bank accounts, credit cards, etc.)
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Professional UI**: Clean, tool-grade interface following modern design principles

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **date-fns** - Date utilities
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── ui/          # Base UI components (Button, Input, Card, etc.)
│   │   └── Layout.tsx   # App layout with navigation
│   ├── lib/             # Utilities and API client
│   │   └── api.ts       # API integration layer
│   ├── pages/           # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Transactions.tsx
│   │   ├── Categories.tsx
│   │   ├── Sources.tsx
│   │   └── Budgets.tsx
│   ├── store/           # State management
│   │   ├── authStore.ts # Authentication state
│   │   └── uiStore.ts   # UI state (toasts, modals, loading)
│   ├── types/           # TypeScript types
│   │   └── api.ts       # API types
│   ├── App.tsx          # Root component with routing
│   ├── main.tsx         # App entry point
│   └── index.css        # Global styles and design tokens
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Design System

The UI follows a professional, tool-grade design system with:

- **Color System**: Primary, secondary, accent, semantic colors
- **Typography**: Inter font family with consistent sizing
- **Spacing**: 4px base unit with 8-point grid
- **Components**: Buttons, inputs, cards, badges, modals, tables
- **Dark patterns avoided**: No unnecessary gradients, shadows, or decorative elements

### Color Palette

```css
Primary:   #2563EB (actions, links)
Secondary: #1E1B4B (navigation, headers)
Accent:    #7C3AED (highlights)
Success:   #15803D (positive states)
Warning:   #C2410C (attention)
Error:     #DC2626 (destructive actions)
Info:      #0369A1 (informational)
```

## Key Features

### Authentication
- JWT token-based authentication
- Token stored in localStorage
- Automatic token refresh on API calls
- Protected routes

### Dashboard
- Monthly income/expense summary
- Top spending categories with progress bars
- Recent transactions list
- Real-time calculations

### Transactions
- Advanced filtering (date range, category, source, type)
- Add/edit modal with validation
- Delete with confirmation
- Inline search
- Responsive table view

### Categories & Sources
- CRUD operations
- Card-based grid layout
- Type-based organization (income/expense categories)
- Empty states with helpful messages

## API Integration

The frontend connects to the backend API at `/api/v1/*`. The Vite dev server proxies API requests to `http://localhost:8000`.

All API calls include:
- Automatic JWT token injection
- Error handling with user-friendly messages
- Loading states
- Success/error toasts

## Accessibility

- Semantic HTML
- ARIA labels on icon buttons
- Keyboard navigation support
- Focus indicators
- Reduced motion support
- Form validation with error messages

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Code Style

- TypeScript strict mode enabled
- Functional components with hooks
- Component composition over prop drilling
- Consistent naming conventions

### State Management

- **Zustand** for global state (auth, UI)
- Local state for component-specific data
- API calls in pages, not in stores

### Error Handling

All async operations wrapped in try/catch with:
- User-friendly error toasts
- Loading states
- Graceful fallbacks

## Contributing

1. Follow the existing code style
2. Use TypeScript types consistently
3. Test on multiple screen sizes
4. Ensure accessibility standards

## License

MIT
