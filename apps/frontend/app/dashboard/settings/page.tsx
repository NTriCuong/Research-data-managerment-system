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
import { useAppSelector } from "@/store/hooks"
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
          <TypographyH1>Thong tin ca nhan</TypographyH1>
          <TypographyMuted className="mt-1">
            Xem thong tin tai khoan, vai tro va don vi dang duoc gan trong he thong.
          </TypographyMuted>
        </div>

        <Button asChild variant="outline">
          <Link href="/change-password">
            <KeyRound size={16} />
            Doi mat khau
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
          <TypographyH2>Ho so tai khoan</TypographyH2>
          <TypographyMuted className="mt-1">Thong tin nay duoc lay tu phien dang nhap hien tai.</TypographyMuted>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <InfoRow icon={UserRound} label="Ho ten" value={currentUser?.full_name ?? "-"} />
          <InfoRow icon={Mail} label="Email" value={currentUser?.email ?? "-"} />
          <InfoRow icon={IdCard} label="Ten dang nhap" value={currentUser?.username ?? "-"} />
          <InfoRow icon={ShieldCheck} label="Vai tro" value={currentUser?.role_name ?? "-"} />
          <InfoRow icon={Building2} label="Don vi" value={currentUser?.department_name ?? "Chua co don vi"} />
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <TypographyH2>Bao mat tai khoan</TypographyH2>
        <TypographyP className="mt-2 max-w-2xl">
          Neu thong tin ca nhan hoac don vi chua dung, vui long lien he quan tri vien de cap nhat tai khoan. Mat khau co the
          duoc thay doi bang luong xac thuc rieng cua he thong.
        </TypographyP>
      </section>
    </div>
  )
}
