export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-zinc-100 flex flex-col items-center justify-center px-4">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-800">RDMS</h1>
        <p className="text-sm text-zinc-500 mt-1">Research Data Management System</p>
      </div>

      <div className="w-full max-w-sm bg-white rounded-xl shadow-sm border border-zinc-200 p-8">
        {children}
      </div>

      <p className="mt-6 text-xs text-zinc-400">© {new Date().getFullYear()} RDMS. All rights reserved.</p>
    </div>
  )
}
