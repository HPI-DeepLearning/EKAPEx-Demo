import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from "@/components/ui/toaster"
import {Provider} from "react-redux";
import {store} from "@/lib/rdx/Store";

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'EKAPEx Weather - AI-Powered Forecasting',
  description: 'Advanced AI-powered weather prediction and visualization platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning>

        <div className="min-h-screen flex flex-col">
          {children}
        </div>
        <Toaster/>
      </body>
    </html>
  )
}

