# Sarah AI Frontend

## Description

The frontend application for Sarah AI Companion, built with Next.js 14, React 18, TypeScript, and Tailwind CSS. It provides an intuitive interface for character creation and a seamless multi-modal chat experience with real-time WebSocket streaming.

## Features

- **Character Management**: Create and customize AI companions with unique personalities
- **Real-time Chat**: WebSocket-based streaming chat with token-by-token responses
- **Multi-modal Support**: Text, voice, and image generation capabilities
- **Sentiment Analysis**: Visual feedback on conversation emotional tone
- **Modern UI**: Beautiful, responsive design with dark mode support

## Configuration

### Environment Variables

Create a `.env.local` file:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8080/api
NEXT_PUBLIC_WS_URL=ws://localhost:8080

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_IMAGES=true
```

### Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000)

### Running with Docker

```bash
docker build -t sarah-frontend .
docker run -p 3000:3000 --env-file .env.local sarah-frontend
```

## Project Structure

```
src/
├── app/                    # Next.js 14 app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── chat/              # Chat interface
│   └── character/         # Character management
├── components/            # React components
│   ├── ui/               # Base UI components
│   ├── chat/             # Chat-specific components
│   └── character/        # Character-specific components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
├── store/                # Zustand state management
└── types/                # TypeScript type definitions
```

## Key Components

### Chat Interface
- **WebSocket Integration**: Real-time bidirectional communication
- **Message Streaming**: Token-by-token display with typing indicators
- **Multi-modal Input**: Support for text, voice, and image inputs
- **Sentiment Display**: Visual indicators for emotional tone

### Character Builder
- **Multi-step Form**: Intuitive character creation wizard
- **Trait Selection**: Choose from personality traits and hobbies
- **AI-Powered Generation**: Generate rich personas from keywords
- **Image Upload**: Reference images for visual consistency

### State Management
- **Zustand**: Lightweight state management for characters
- **React Query**: Server state synchronization
- **WebSocket Hook**: Custom hook for chat connectivity

## Development

### Code Style
- TypeScript strict mode enabled
- ESLint configuration for consistency
- Prettier for code formatting

### Testing
```bash
npm run test        # Run tests
npm run test:watch  # Watch mode
npm run test:coverage # Coverage report
```

### Building
```bash
npm run build      # Production build
npm run start      # Production server
npm run lint       # Lint code
npm run type-check # TypeScript validation
```

## Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Inter font with subsetting
- **Caching**: React Query for API responses

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Troubleshooting

### WebSocket Connection Issues
- Verify API Gateway is running
- Check CORS configuration
- Ensure WebSocket upgrade headers

### Build Errors
- Clear `.next` directory
- Delete `node_modules` and reinstall
- Check TypeScript errors with `npm run type-check`

### Performance Issues
- Enable React DevTools Profiler
- Check bundle size with `npm run analyze`
- Monitor WebSocket message frequency
