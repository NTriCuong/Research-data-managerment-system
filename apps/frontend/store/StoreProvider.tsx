'use client'

import { setupInterceptors } from '@/lib/axios/interceptor'
import { useRef } from 'react'
import { Provider } from 'react-redux'
import { makeStore, type AppStore } from './store'
import AuthInitializer from './AuthInitializer'

export default function StoreProvider({ children }: { children: React.ReactNode }) {
  const storeRef = useRef<AppStore | null>(null)
  if (!storeRef.current) {
    storeRef.current = makeStore()
    setupInterceptors(storeRef.current)
  }
  return (
    <Provider store={storeRef.current}>
      <AuthInitializer />
      {children}
    </Provider>
  )
}
