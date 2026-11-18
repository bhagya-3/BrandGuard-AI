import { BrowserRouter } from 'react-router-dom'
import { ErrorBoundary } from './components/shared.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import { NotificationProvider } from './context/NotificationContext.jsx'
import { WorkspaceProvider } from './context/WorkspaceContext.jsx'
import AppRoutes from './routes/AppRoutes.jsx'

export default function App() {
  return (
    <AuthProvider>
      <WorkspaceProvider>
        <NotificationProvider>
          <BrowserRouter>
            <ErrorBoundary><AppRoutes /></ErrorBoundary>
          </BrowserRouter>
        </NotificationProvider>
      </WorkspaceProvider>
    </AuthProvider>
  )
}
