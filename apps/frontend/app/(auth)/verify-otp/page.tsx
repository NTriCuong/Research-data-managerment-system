'use client'

import { parseAxiosError } from '@/lib/axios/error-paser'
import { authService } from '@/services/auth/auth.service'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useRef, useState } from 'react'
import { toast } from 'sonner'

const OTP_LENGTH = 6

function VerifyOtpForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const flow = searchParams.get('flow') // 'change-password' hiện tại; sau này có thể thêm flow khác

  const [digits, setDigits] = useState<string[]>(Array(OTP_LENGTH).fill(''))
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const handleChange = (index: number, value: string) => {
    if (!/^\d?$/.test(value)) return
    const next = [...digits]
    next[index] = value
    setDigits(next)
    if (value && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH)
    const next = [...digits]
    pasted.split('').forEach((char, i) => { next[i] = char })
    setDigits(next)
    inputRefs.current[Math.min(pasted.length, OTP_LENGTH - 1)]?.focus()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const otp = digits.join('')
    if (otp.length < OTP_LENGTH) {
      setError('Vui lòng nhập đủ 6 số OTP')
      return
    }
    setError('')
    setLoading(true)
    try {
      if (flow === 'change-password') {
        await authService.confirmChangePassword(otp)
        toast.success('Xác thực thành công, đổi mật khẩu hoàn tất')
        setTimeout(() => {
          router.push('/auth/login')
        }, 1000)
        return // không setLoading(false) ngay, giữ trạng thái loading trong lúc chờ redirect
      }
    } catch (err) {
      setError(parseAxiosError(err).message)
      setLoading(false)
    }
  }

  return (
    <>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-zinc-800">Xác thực OTP</h2>
        <p className="text-sm text-zinc-500 mt-1">
          Nhập mã 6 số đã được gửi đến email của bạn
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex justify-between gap-2" onPaste={handlePaste}>
          {digits.map((digit, i) => (
            <input
              key={i}
              ref={(el) => { inputRefs.current[i] = el }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              className="w-10 h-12 text-center text-lg font-semibold rounded-lg border border-zinc-300 bg-white text-zinc-900 outline-none focus:ring-2 focus:ring-zinc-400 focus:border-transparent transition"
            />
          ))}
        </div>

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
          {loading ? 'Đang xác thực...' : 'Xác nhận'}
        </button>
      </form>
    </>
  )
}

export default function VerifyOtpPage() {
  return (
    <Suspense fallback={null}>
      <VerifyOtpForm />
    </Suspense>
  )
}