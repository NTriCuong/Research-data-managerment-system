import type { ComponentPropsWithoutRef, ElementType, ReactNode } from "react"

import { cn } from "@/lib/utils"

type TypographyProps<T extends ElementType> = {
  as?: T
  children: ReactNode
  className?: string
} & Omit<ComponentPropsWithoutRef<T>, "as" | "children" | "className">

function TypographyH1<T extends ElementType = "h1">({
  as,
  className,
  children,
  ...props
}: TypographyProps<T>) {
  const Comp = as ?? "h1"

  return (
    <Comp
      className={cn("scroll-m-20 text-2xl font-semibold tracking-normal text-gray-900", className)}
      {...props}
    >
      {children}
    </Comp>
  )
}

function TypographyH2<T extends ElementType = "h2">({
  as,
  className,
  children,
  ...props
}: TypographyProps<T>) {
  const Comp = as ?? "h2"

  return (
    <Comp className={cn("text-base font-semibold tracking-normal text-gray-900", className)} {...props}>
      {children}
    </Comp>
  )
}

function TypographyP<T extends ElementType = "p">({
  as,
  className,
  children,
  ...props
}: TypographyProps<T>) {
  const Comp = as ?? "p"

  return (
    <Comp className={cn("text-sm leading-6 text-gray-600", className)} {...props}>
      {children}
    </Comp>
  )
}

function TypographyMuted<T extends ElementType = "p">({
  as,
  className,
  children,
  ...props
}: TypographyProps<T>) {
  const Comp = as ?? "p"

  return (
    <Comp className={cn("text-sm text-gray-500", className)} {...props}>
      {children}
    </Comp>
  )
}

function TypographySmall<T extends ElementType = "small">({
  as,
  className,
  children,
  ...props
}: TypographyProps<T>) {
  const Comp = as ?? "small"

  return (
    <Comp className={cn("text-xs font-medium leading-none text-gray-500", className)} {...props}>
      {children}
    </Comp>
  )
}

export { TypographyH1, TypographyH2, TypographyMuted, TypographyP, TypographySmall }
