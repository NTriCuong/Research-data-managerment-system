'use client'

import { authService } from '@/services/auth/auth.service'
import { setCredentials } from '@/store/slice/auth.slice'
import { useAppDispatch } from '@/store/hooks'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { getRoleHomePath } from '@/lib/auth/routes'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function LoginPage() {
  const dispatch = useAppDispatch()
  const router = useRouter()

  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await authService.login(identifier, password)
      dispatch(setCredentials({ user: data.user, accessToken: data.access_token }))
      router.push(getRoleHomePath(data.user.role_name))
    } catch (err) {
      const appError = parseAxiosError(err)
      console.log(appError);

      setError(appError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-zinc-800">Đăng nhập</h2>
        <p className="text-sm text-zinc-500 mt-1">Nhập thông tin đăng nhập của bạn để tiếp tục</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">
            Username or email
          </label>
          <input
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
            autoFocus
            placeholder="Enter username or email"
            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-300 bg-white text-zinc-900 placeholder-zinc-400 outline-none focus:ring-2 focus:ring-zinc-400 focus:border-transparent transition"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="Enter password"
            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-300 bg-white text-zinc-900 placeholder-zinc-400 outline-none focus:ring-2 focus:ring-zinc-400 focus:border-transparent transition"
          />
        </div>

        {error && (
          <p className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        <div className="text-right">
          <Link
            href="/change-password"
            className="text-sm text-zinc-500 hover:text-zinc-800 hover:underline transition"
          >
            Quên mật khẩu?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 text-sm font-medium rounded-lg bg-zinc-800 text-white hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </>
  )
}
