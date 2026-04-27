# Expense Tracker - Frontend Setup Guide

## Quick Start

To run the frontend application:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at **http://localhost:3000**

## Prerequisites

Before running the frontend, ensure:

1. **Node.js 18+** is installed
2. **Backend API** is running on `http://localhost:8000`
3. Backend database is set up and migrations are applied

## Project Overview

This is a modern, professional frontend built with:

- **React 18** + **TypeScript** for type-safe UI development
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for utility-first styling
- **Zustand** for lightweight state management
- **React Router** for client-side navigation

## Architecture

### Pages

1. **Authentication**
   - `/login` - User login
   - `/register` - New user registration

2. **Protected Pages** (requires authentication)
   - `/dashboard` - Overview with analytics and charts
   - `/transactions` - Full transaction management with filters
   - `/categories` - Manage expense/income categories
   - `/sources` - Manage financial sources (banks, cards)
   - `/budgets` - Budget tracking (coming soon)

### Components

**UI Components** (`src/components/ui/`):
- `Button` - Primary, secondary, ghost, destructive variants
- `Input` - Text inputs with labels and validation
- `Select` - Custom dropdown with styling
- `Card` - Container component with hover states
- `Badge` - Status indicators
- `Toast` - Non-blocking notifications
- `ConfirmDialog` - Confirmation prompts
- `LoadingOverlay` - Full-page loading state
- `EmptyState` - Placeholder for empty lists

**Layout** (`src/components/Layout.tsx`):
- Top navigation bar with active state indicators
- Responsive navigation menu
- Logout functionality
- Global UI components (toasts, modals)

### State Management

**Auth Store** (`src/store/authStore.ts`):
- JWT token management
- Authentication state
- localStorage persistence

**UI Store** (`src/store/uiStore.ts`):
- Toast notifications
- Loading overlay
- Confirmation dialogs
- Global UI state

### API Integration

**API Client** (`src/lib/api.ts`):
- Axios-based HTTP client
- Automatic token injection
- Error handling with 401 redirects
- Type-safe API methods

**API Methods**:
```typescript
authApi.register()
authApi.login()

categoriesApi.getAll()
categoriesApi.create()
categoriesApi.update()
categoriesApi.delete()

sourcesApi.getAll()
sourcesApi.create()
sourcesApi.update()
sourcesApi.delete()

transactionsApi.getAll()
transactionsApi.getById()
transactionsApi.create()
transactionsApi.update()
transactionsApi.delete()
```

## Design System

### Color System

Following the professional-frontend-development skill:

```css
/* Primary Actions */
--color-primary: #2563EB
--color-primary-hover: #1D4ED8

/* Navigation & Headers */
--color-secondary: #1E1B4B

/* Links & Highlights */
--color-accent: #7C3AED

/* Status Colors */
--color-success: #15803D
--color-warning: #C2410C
--color-error: #DC2626
--color-info: #0369A1

/* Neutral Palette */
--color-neutral-950: #0A0A0A (headings)
--color-neutral-800: #262626 (body text)
--color-neutral-600: #525252 (secondary text)
--color-neutral-200: #E5E5E5 (borders)
--color-neutral-100: #F5F5F5 (subtle fills)
```

### Typography

- **Font**: Inter (Google Fonts)
- **Page Title**: 24px, 700 weight
- **Section Title**: 18px, 600 weight
- **Card Title**: 15px, 600 weight
- **Body**: 14px, 400/500 weight
- **Label**: 12px, 600 weight, uppercase
- **Caption**: 12px, 400 weight

### Spacing

Based on 4px unit:
- Small gaps: 4px, 8px
- Medium gaps: 12px, 16px
- Large gaps: 24px, 32px
- Section padding: 32px (x) × 24px (y)

## Features

### Dashboard
- **Summary Cards**: Total income, expenses, net balance
- **Top Categories**: Visual breakdown of spending by category
- **Recent Transactions**: Last 5 transactions with quick view
- **Monthly View**: Filtered to current month by default

### Transactions
- **Advanced Filters**: Date range, category, source, type, search
- **Add/Edit Modal**: Full-featured form with validation
- **Table View**: Sortable, responsive table with inline actions
- **Delete Confirmation**: Safety prompt before deletion
- **Amount Display**: Formatted with cents handling ($XX.XX)

### Categories
- **Dual Organization**: Separate expense and income categories
- **Card Grid**: Responsive grid layout (3 columns on desktop)
- **Type Indicators**: Color-coded badges for income/expense
- **Quick Actions**: Edit and delete from card

### Sources
- **Source Types**: Bank, credit card, cash, investment, other
- **Description Field**: Optional additional details
- **Creation Date**: Track when sources were added

## User Experience

### Loading States
- Skeleton loaders for lists and cards
- Button spinners during async operations
- Full-page overlay for critical operations

### Error Handling
- Toast notifications for all errors
- Field-level validation errors
- Confirmation dialogs for destructive actions
- Automatic retry on 401 (token expiry)

### Empty States
- Descriptive messages for empty lists
- Clear call-to-action buttons
- Helpful icons for visual clarity

## Development Commands

```bash
# Start dev server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
tsc --noEmit

# Linting
npm run lint
```

## Environment Configuration

The frontend expects the backend API at `http://localhost:8000`.

To change the API URL, edit `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url',
      changeOrigin: true,
    },
  },
}
```

## Building for Production

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. The `dist/` folder contains the optimized static files

3. Serve with any static file server:
```bash
# Using Python
python -m http.server --directory dist 3000

# Using Node.js serve
npx serve dist -p 3000
```

## Deployment

### Option 1: Static Hosting (Vercel, Netlify, S3)
1. Build: `npm run build`
2. Deploy `dist/` folder
3. Set backend API URL in proxy or environment

### Option 2: Docker
```dockerfile
FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Option 3: Serve with Backend
Place the `dist/` contents in your backend's static files directory.

## Accessibility Features

✓ Semantic HTML elements  
✓ ARIA labels on icon buttons  
✓ Keyboard navigation support  
✓ Focus indicators on all interactive elements  
✓ Form labels properly associated  
✓ Error messages linked to fields  
✓ Reduced motion support  
✓ Minimum 44×44px touch targets  

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Tips for Customization

### Change Brand Colors
Edit `tailwind.config.js` and `src/index.css`:
```javascript
colors: {
  primary: {
    DEFAULT: '#YOUR_COLOR',
    hover: '#DARKER_SHADE',
    // ...
  }
}
```

### Add New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/Layout.tsx`

### Modify API Base URL
Edit `src/lib/api.ts`:
```typescript
const API_BASE_URL = '/api/v1' // or full URL for different domain
```

## Troubleshooting

**Issue**: API calls fail with CORS errors  
**Solution**: Ensure backend has CORS enabled for `http://localhost:3000`

**Issue**: Login succeeds but redirects to login  
**Solution**: Check localStorage for `access_token`. Clear browser cache.

**Issue**: Styles not applying  
**Solution**: Restart dev server. Check Tailwind config.

**Issue**: TypeScript errors  
**Solution**: Run `npm install` to ensure types are installed

## Next Steps

1. **Install dependencies**: `npm install`
2. **Start backend**: Ensure API is running on port 8000
3. **Start frontend**: `npm run dev`
4. **Register user**: Go to /register
5. **Add data**: Create categories, sources, transactions
6. **Explore dashboard**: View analytics and summaries

## Support

For issues or questions:
- Check backend logs for API errors
- Check browser console for frontend errors
- Verify network requests in DevTools
- Ensure backend database is properly configured

---

**Built with React, TypeScript, and modern web standards** 🚀
