import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Code Review Tool by Kuriyam',
  description: 'A powerful code review tool by Kuriyam',
  generator: 'Kuriyam',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
