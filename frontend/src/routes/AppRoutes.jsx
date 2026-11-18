import { Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import AdminLayout from '../layouts/AdminLayout.jsx'
import AuthLayout from '../layouts/AuthLayout.jsx'
import DashboardLayout from '../layouts/DashboardLayout.jsx'
import PublicLayout from '../layouts/PublicLayout.jsx'
import { LoadingSpinner } from '../components/shared.jsx'
import RoleRoutes from './RoleRoutes.jsx'
import {
  adminRoutes,
  authRoutes,
  errorRoutes,
  publicRoutes,
  workspaceRoutes,
} from './routeConfig.js'

function RoutePage({ Component }) {
  return <Suspense fallback={<LoadingSpinner label="Loading page" />}><Component /></Suspense>
}

export default function AppRoutes() {
  const notFound = errorRoutes.find((route) => route.key.endsWith('/NotFoundPage'))?.Component
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        {publicRoutes.map(({ path, Component, key }) => <Route key={key} path={path} element={<RoutePage Component={Component} />} />)}
      </Route>
      <Route element={<AuthLayout />}>
        {authRoutes.map(({ path, Component, key }) => <Route key={key} path={path} element={<RoutePage Component={Component} />} />)}
      </Route>
      <Route element={<RoleRoutes />}>
        <Route element={<DashboardLayout />}>
          {workspaceRoutes.map(({ path, Component, key }) => <Route key={key} path={path} element={<RoutePage Component={Component} />} />)}
        </Route>
      </Route>
      <Route element={<RoleRoutes minimumRole="admin" />}>
        <Route element={<AdminLayout />}>
          {adminRoutes.map(({ path, Component, key }) => <Route key={key} path={path} element={<RoutePage Component={Component} />} />)}
        </Route>
      </Route>
      {errorRoutes.map(({ path, Component, key }) => <Route key={key} path={path} element={<RoutePage Component={Component} />} />)}
      <Route path="*" element={<RoutePage Component={notFound} />} />
    </Routes>
  )
}
