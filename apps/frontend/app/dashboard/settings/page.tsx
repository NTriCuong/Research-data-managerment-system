"use client"

import Link from "next/link"
import { Building2, IdCard, KeyRound, Mail, ShieldCheck, UserRound } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  TypographyH1,
  TypographyH2,
  TypographyMuted,
  TypographyP,
  TypographySmall,
} from "@/components/ui/typography"
import { useAppSelector } from "@/lib/hooks/hooks"
import { selectCurrentUser } from "@/store/slice/auth.slice"

function getInitials(name?: string) {
  if (!name) return "U"

  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
}

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof UserRound
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gray-50 text-gray-500">
        <Icon size={16} />
      </div>
      <div className="min-w-0">
        <TypographySmall as="p">{label}</TypographySmall>
        <TypographyP className="mt-1 truncate font-medium text-gray-900">{value}</TypographyP>
      </div>
    </div>
  )
}

export default function PersonalSettingsPage() {
  const currentUser = useAppSelector(selectCurrentUser)

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <TypographyH1>Cài đặt thông tin cá nhân</TypographyH1>
          <TypographyMuted className="mt-1">
            Xem thông tin tài khoản, vai trò và đơn vị đang được gắn trong hệ thống.
          </TypographyMuted>
        </div>

        <Button asChild variant="outline">
          <Link href="/change-password">
            <KeyRound size={16} />
            Đổi mật khẩu
          </Link>
        </Button>
      </div>

      <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-4">
          <Avatar size="lg" className="size-16">
            <AvatarFallback className="text-lg font-semibold">
              {getInitials(currentUser?.full_name)}
            </AvatarFallback>
          </Avatar>

          <div className="min-w-0">
            <TypographyH2>{currentUser?.full_name ?? "Nguoi dung"}</TypographyH2>
            <TypographyMuted className="mt-1">{currentUser?.email ?? "Chua co email"}</TypographyMuted>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <div>
          <TypographyH2>Thông tin chi tiết</TypographyH2>
          <TypographyMuted className="mt-1">Thay đổi thông tin cá nhân của bạn đang được cập nhật.</TypographyMuted>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <InfoRow icon={UserRound} label="Họ và tên" value={currentUser?.full_name ?? "-"} />
          <InfoRow icon={Mail} label="Email" value={currentUser?.email ?? "-"} />
          <InfoRow icon={IdCard} label="ên đăng nhập" value={currentUser?.username ?? "-"} />
          <InfoRow icon={ShieldCheck} label="Vai trò" value={currentUser?.role_name ?? "-"} />
          <InfoRow icon={Building2} label="Đơn vị" value={currentUser?.department_name ?? "Chưa có đơn vị"} />
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <TypographyH2>Bảo mật tài khoản</TypographyH2>
        <TypographyP className="mt-2 max-w-2xl">
          Nếu thông tin cá nhân hoặc đơn vị chưa đúng, vui lòng liên hệ quản trị viên để cập nhật tài khoản.
        </TypographyP>
        <TypographyP className="mt-2 max-w-2xl">
          Email: <a href="mailto:admin@example.com" className="text-blue-500 hover:underline">
            admin@example.com
          </a>
          </TypographyP>
      </section>
    </div>
  )
}
