# Smart Lecture Assistant - Frontend

React + TypeScript frontend for the Smart Lecture Assistant application.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file in the frontend directory:

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at: http://localhost:5173

## Build for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   ├── pages/           # Page components
│   ├── services/        # API client and services
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML entry point
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

## Technology Stack

- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **React Query**: Server state management
- **Axios**: HTTP client
- **React Flow**: Interactive node-based graphs for topic maps
- **Recharts**: Data visualization
- **React Dropzone**: File upload interface

## Development

### Code Linting

```bash
npm run lint
```

### Type Checking

TypeScript type checking is run automatically during build. To check types manually:

```bash
npx tsc --noEmit
```

## Features

- **Dashboard**: Overview of all lectures and topics
- **Upload Interface**: Drag-and-drop PDF upload with metadata
- **Topic Map**: Interactive visualization of cross-lecture topics
- **Timeline View**: Week-by-week topic appearances
- **Q&A Interface**: RAG-based question answering
- **Summary Viewer**: Topic summaries with source citations

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`. All API calls are made through the centralized `api.ts` service located in `src/services/`.

## Future Enhancements

- Real-time upload progress tracking
- Advanced topic filtering and search
- Export functionality for summaries
- User authentication and multi-user support
- Mobile responsive design
