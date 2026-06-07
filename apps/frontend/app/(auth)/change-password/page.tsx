'use client'

import axiosInstance from '@/lib/axios/axios.instance'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { API_ENDPOINT } from '@/lib/constants/api-endpoint'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function ChangePasswordPage() {
  const router = useRouter()

  const [form, setForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (form.new_password !== form.confirm_password) {
      setError('New passwords do not match')
      return
    }

    setLoading(true)
    try {
      await axiosInstance.post(API_ENDPOINT.AUTH.CHANGE_PASSWORD, {
        current_password: form.current_password,
        new_password: form.new_password,
      })
      router.push('/auth/login')
    } catch (err) {
      setError(parseAxiosError(err).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-zinc-800">Change password</h2>
        <p className="text-sm text-zinc-500 mt-1">Update your account password</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {(
          [
            { name: 'current_password', label: 'Current password' },
            { name: 'new_password', label: 'New password' },
            { name: 'confirm_password', label: 'Confirm new password' },
          ] as const
        ).map(({ name, label }) => (
          <div key={name}>
            <label className="block text-sm font-medium text-zinc-700 mb-1">
              {label}
            </label>
            <input
              type="password"
              name={name}
              value={form[name]}
              onChange={handleChange}
              required
              placeholder={`Enter ${label.toLowerCase()}`}
              className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-300 bg-white text-zinc-900 placeholder-zinc-400 outline-none focus:ring-2 focus:ring-zinc-400 focus:border-transparent transition"
            />
          </div>
        ))}

        {error && (
          <p className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 text-sm font-medium rounded-lg bg-zinc-800 text-white hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Updating...' : 'Update password'}
        </button>

        <button
          type="button"
          onClick={() => router.back()}
          className="w-full py-2 px-4 text-sm font-medium rounded-lg border border-zinc-300 text-zinc-600 hover:bg-zinc-50 transition"
        >
          Cancel
        </button>
      </form>
    </>
  )
}
