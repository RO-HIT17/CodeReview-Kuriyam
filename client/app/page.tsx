"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import { Mail, Lock, Eye, EyeOff, LogIn } from "lucide-react"

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    const formData = new FormData(e.currentTarget)
    const email = formData.get('email') as string
    const password = formData.get('password') as string

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('name', data.name)
        localStorage.setItem('token', data.token)
        localStorage.setItem("user_id", data.user_id)
        localStorage.setItem("github_installation_id", data.github_installation_id) 
        toast({ title: "Success", description: "Logged in successfully!", variant: "default" })
        router.push('/dashboard') 
      } else {
        const errorData = await response.json()
        toast({ title: "Error", description: errorData.message || 'Login failed', variant: "destructive" })
      }
    } catch (error) {
      toast({ title: "Error", description: 'Network error. Please try again.', variant: "destructive" })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-gray-100 to-gray-200 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md bg-white border border-teal-200 shadow-[0_4px_24px_0_rgba(20,184,166,0.08)]">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center gap-3 mb-2">
            <img src="/image.png" alt="Kuriyam Logo" className="h-9 w-9 object-contain" />
            <CardTitle className="text-2xl font-bold text-teal-700">Kuriyam Code Review</CardTitle>
          </div>
          <CardDescription className="text-center">
            Sign in to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Input id="email" name="email" type="email" placeholder="john@example.com" required className="pl-10" />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>
            </div>
            <div className="space-y-2 relative">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input id="password" name="password" type={showPassword ? "text" : "password"} placeholder="Enter your password" required className="pl-10 pr-10" />
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-teal-700 hover:underline" onClick={() => setShowPassword(v => !v)} tabIndex={-1}>
                  {showPassword ? <EyeOff className="h-5 w-5 text-teal-700" /> : <Eye className="h-5 w-5 text-teal-700" />}
                </button>
              </div>
            </div>
            <Button type="submit" className="w-full flex items-center justify-center gap-2" disabled={isLoading}>
              <LogIn className="h-5 w-5 text-teal-700" />
              {isLoading ? "Signing In..." : "Sign In"}
            </Button>
          </form>

          <Separator className="my-6" />

          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">Don't have an account?</p>
            <Link href="/register">
              <Button variant="outline" className="w-full">
                Create Account
              </Button>
            </Link>
          </div>
          <div className="text-center mt-4">
            <Link href="/admin/login">
              <Button variant="ghost" size="sm" className="text-xs text-muted-foreground hover:text-primary">Admin Login</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
