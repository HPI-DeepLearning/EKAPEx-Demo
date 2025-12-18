# EKAPEx Weather UI

The frontend application of the EKAPEx Weather Demo project. A modern, interactive web interface built with Next.js 15 for visualizing and comparing AI weather forecasting models.

## Overview

This is the frontend component of the EKAPEx Weather Demo project. It provides an intuitive user interface for exploring weather forecast data from multiple AI models (GraphCast, Cerrora), enabling users to visualize weather patterns, compare model predictions, and analyze forecast accuracy through interactive maps and dashboards.

## Features

- **Interactive Weather Maps**: Zoom and pan functionality for detailed weather data exploration
- **Model Comparison Dashboard**: Side-by-side comparison of different weather forecasting models
- **Inference Comparison**: Compare model predictions with ground truth data
- **Time-based Selection**: Navigate through different forecast time ranges
- **Metrics Visualization**: Performance metrics and accuracy statistics with interactive charts
- **Extreme Events Dataset**: Integrated dataset for analyzing severe weather patterns
- **Responsive Design**: Modern UI with Tailwind CSS and shadcn/ui components
- **Real-time Updates**: Live data fetching with React Query

## Technology Stack

### Core Framework
- **Next.js 15.1.4**: React framework with App Router
- **React 19**: Latest React with concurrent features
- **TypeScript 5**: Type-safe development

### State Management & Data Fetching
- **Redux Toolkit 2.8.2**: Global state management
- **TanStack React Query 5.64.0**: Server state management and caching
- **React Redux 9.2.0**: React bindings for Redux

### UI Components & Styling
- **Tailwind CSS 3.4.1**: Utility-first CSS framework
- **shadcn/ui**: High-quality UI components (Radix UI primitives)
  - Dialog, Select, Separator, Slider, Toast, Tooltip
- **Lucide React**: Icon library
- **class-variance-authority**: Component variants
- **tailwind-merge**: Conditional class merging

### Visualization & Interaction
- **Recharts 3.1.2**: Charts and data visualization
- **react-zoom-pan-pinch 3.7.0**: Image zoom and pan functionality
- **date-fns 4.1.0**: Date manipulation and formatting

### Development Tools
- **ESLint**: Code linting
- **PostCSS**: CSS processing

## Prerequisites

Before setting up the frontend, ensure you have:

- **Node.js 18+**: JavaScript runtime ([Download Node.js](https://nodejs.org/))
- **npm, yarn, pnpm, or bun**: Package manager (npm comes with Node.js)
- **Backend API**: The weather_api backend service must be running (see [Backend README](../weather_api/README.md))

## Project Structure

```
weather_ui/
│
├── app/                          # Next.js App Router
│   ├── page.tsx                  # Home page
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   ├── dashboard/                # Dashboard page
│   │   └── page.tsx
│   ├── inference_compare/        # Inference comparison page
│   │   └── page.tsx
│   ├── api-docs/                 # API documentation page
│   │   └── page.tsx
│   ├── api/                      # API routes
│   │   └── weather-app/
│   └── Utilities/                # Application utilities
│       ├── ApplicationInterfaces.ts
│       └── Utilities.ts
│
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── select.tsx
│   │   ├── slider.tsx
│   │   └── ...
│   ├── weather-map.tsx           # Main weather map component
│   ├── weather-sidebar.tsx       # Sidebar navigation
│   ├── ModelComparisonDashboard.tsx
│   ├── MetricsReporting.tsx
│   ├── ImageZoom.tsx             # Image zoom components
│   ├── SynchronizedImageZoom.tsx
│   ├── BarChrt.tsx               # Chart components
│   ├── LIneChrt.tsx
│   └── ...
│
├── lib/                          # Library code
│   ├── api-client.ts             # API client for backend communication
│   ├── utils.ts                  # Utility functions
│   └── rdx/                      # Redux store
│       ├── Store.ts              # Redux store configuration
│       └── WeatherSlice.ts       # Weather state slice
│
├── hooks/                        # Custom React hooks
├── public/                       # Static assets
│
├── extreme_events_dataset.json   # Extreme weather events data
├── components.json               # shadcn/ui configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── next.config.ts                # Next.js configuration
├── package.json                  # Dependencies and scripts
└── README.md                     # This documentation
```

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/HPI-DeepLearning/EKAPEx-Demo.git
cd EKAPEx-Demo/weather_ui
```

### Step 2: Install Dependencies

Choose your preferred package manager:

```bash
# Using npm (recommended)
npm install

# Or using yarn
yarn install

# Or using pnpm
pnpm install

# Or using bun
bun install
```

This will install all dependencies listed in `package.json`, including:
- Next.js and React
- UI components (Radix UI, shadcn/ui)
- State management (Redux, React Query)
- Visualization libraries (Recharts)
- Styling tools (Tailwind CSS)

### Step 3: Configure Environment Variables

Create a `.env.local` file in the project root:

```bash
touch .env.local
```

Add the following environment variables:

```bash
# Backend API base URL (adjust host/port as needed)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8999/api/v1

# Backend image serving URL
NEXT_PUBLIC_IMAGE_BASE_URL=http://localhost:8999/backend-fast-api/streaming
```

**Configuration Notes:**
- `NEXT_PUBLIC_API_BASE_URL`: Points to your backend API endpoint
- `NEXT_PUBLIC_IMAGE_BASE_URL`: Points to the backend's static image serving endpoint
- Replace `localhost:8999` with your backend server address if different
- For production deployments, use your production backend URLs

**Example configurations:**

Development (local backend):
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8999/api/v1
NEXT_PUBLIC_IMAGE_BASE_URL=http://localhost:8999/backend-fast-api/streaming
```

Production (remote backend):
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-domain.com/api/v1
NEXT_PUBLIC_IMAGE_BASE_URL=https://your-domain.com/backend-fast-api/streaming
```

## Usage

### Development Server

Start the development server with hot-reload:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

The application will be available at **[http://localhost:3000](http://localhost:3000)**.

Features in development mode:
- Hot Module Replacement (HMR)
- Fast Refresh for instant updates
- Detailed error messages
- Source maps for debugging

### Building for Production

Create an optimized production build:

```bash
npm run build
```

This will:
- Create an optimized production build in `.next/` directory
- Minimize JavaScript and CSS
- Optimize images and fonts
- Generate static pages where possible

### Running Production Server

After building, start the production server:

```bash
npm run start
```

The production server will run at **[http://localhost:3000](http://localhost:3000)** with optimized performance.

### Linting

Run ESLint to check code quality:

```bash
npm run lint
```

Fix linting issues automatically:

```bash
npm run lint -- --fix
```

## Key Pages and Features

### Main Weather Map (`/`)
- Interactive weather visualization
- Variable selection (temperature, wind, geopotential height, sea level pressure)
- Model selection (GraphCast, Cerrora, Ground Truth)
- Time-based forecast navigation
- Zoom and pan functionality

### Dashboard (`/dashboard`)
- Model comparison overview
- Performance metrics visualization
- Multiple weather parameters side-by-side
- Charts and statistics

### Inference Comparison (`/inference_compare`)
- Side-by-side model predictions vs ground truth
- Synchronized image zoom
- Time slider for temporal comparison
- Difference analysis

### API Documentation (`/api-docs`)
- Backend API endpoint documentation
- Request/response examples

## API Integration

The frontend communicates with the backend through the API client (`lib/api-client.ts`). The client handles:

- **Base Times**: Fetching available forecast initialization times
- **Weather Data**: Retrieving weather map visualizations
- **Model Data**: Accessing predictions from different models
- **Ground Truth**: Loading actual weather observations

Example API usage:

```typescript
import { apiClient } from '@/lib/api-client';

// Fetch available base times
const baseTimes = await apiClient.getBaseTimes('temp_wind');

// Fetch weather data
const weatherData = await apiClient.getWeatherData({
  variableType: 'temp_wind',
  baseTime: 1609459200,
  validTime: [1609459200, 1609462800]
});
```

## State Management

### Redux Store
Global application state is managed with Redux Toolkit:
- Weather variable selection
- Time range selection
- Model selection
- User preferences

### React Query
Server state and caching:
- API data fetching
- Automatic cache management
- Background refetching
- Optimistic updates

## Development Tips

### Adding New Components

This project uses shadcn/ui for component management:

```bash
# Add a new shadcn/ui component
npx shadcn@latest add [component-name]
```

### Custom Hooks

Create custom hooks in the `hooks/` directory for reusable logic.

### Styling

- Use Tailwind CSS utility classes for styling
- Custom styles can be added to `app/globals.css`
- Component-specific styles use Tailwind's `@apply` directive

### Type Safety

- Define interfaces in `app/Utilities/ApplicationInterfaces.ts`
- Use TypeScript for all new components and utilities
- Enable strict mode in `tsconfig.json` for maximum type safety

## Troubleshooting

### Common Issues

**Issue: "Cannot connect to backend API"**
- Ensure the backend server is running (see [Backend README](../weather_api/README.md))
- Verify `NEXT_PUBLIC_API_BASE_URL` in `.env.local` matches your backend URL
- Check for CORS issues if backend is on a different domain

**Issue: "Images not loading"**
- Verify `NEXT_PUBLIC_IMAGE_BASE_URL` is correctly configured
- Ensure backend's `streaming/` directory has proper permissions
- Check browser console for 404 errors

**Issue: "Module not found" errors**
- Delete `node_modules/` and `.next/` directories
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`

**Issue: "Port 3000 already in use"**
- Change the port: `npm run dev -- -p 3001`
- Or kill the process using port 3000

### Performance Optimization

- Images are automatically optimized by Next.js Image component
- Use dynamic imports for heavy components
- Implement React.lazy() for code splitting
- Enable caching in React Query for frequently accessed data

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Integration with Backend

This frontend is designed to work seamlessly with the backend service. Ensure:

1. Backend is running at the configured URL
2. CORS is properly configured on the backend
3. All required environment variables are set
4. Network connectivity between frontend and backend

For backend setup instructions, see the [Backend README](../weather_api/README.md).

For full project overview, see the [Main Project README](../README.md).

## Learn More

### Next.js Resources
- [Next.js Documentation](https://nextjs.org/docs) - Learn about Next.js features and API
- [Learn Next.js](https://nextjs.org/learn) - Interactive Next.js tutorial
- [Next.js GitHub Repository](https://github.com/vercel/next.js)

### Component Libraries
- [shadcn/ui Documentation](https://ui.shadcn.com/) - UI component library
- [Radix UI](https://www.radix-ui.com/) - Headless UI primitives
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

### State Management
- [Redux Toolkit](https://redux-toolkit.js.org/) - Redux state management
- [TanStack Query](https://tanstack.com/query/latest) - Server state management

## Contributing

When contributing to the frontend:
1. Follow the existing code style and structure
2. Use TypeScript for all new code
3. Add proper type definitions
4. Test components in both development and production builds
5. Ensure responsive design works on all screen sizes
6. Update this README if adding major features

## License

See the main project README for license information.

## Acknowledgments

- Built with [Next.js](https://nextjs.org/) by Vercel
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Icons from [Lucide](https://lucide.dev/)
- Charts powered by [Recharts](https://recharts.org/)
