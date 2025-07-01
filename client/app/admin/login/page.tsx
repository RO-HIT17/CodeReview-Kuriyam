"use client";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from "@/components/ui/navigation-menu";
import { Shield, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Label } from "@/components/ui/label";

export default function AdminLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
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
      });
      if (response.ok) {
        const data = await response.json();
        if (data.is_admin) {
          localStorage.setItem("isAdmin", "true");
          localStorage.setItem("token", data.token);
          localStorage.setItem("name", data.name);
          localStorage.setItem("user_id", data.user_id)
          toast({ title: "Success", description: "Admin login successful!", variant: "default" });
          router.push("/admin");
        } else {
          toast({ title: "Access Denied", description: "Admin privileges required.", variant: "destructive" });
        }
      } else {
        const errorData = await response.json();
        toast({ title: "Error", description: errorData.message || "Invalid credentials", variant: "destructive" });
      }
    } catch (error) {
      toast({ title: "Error", description: "Network error. Please try again.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-gray-100 to-gray-200 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md bg-white border border-teal-200 shadow-[0_4px_24px_0_rgba(20,184,166,0.08)]">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center gap-3 mb-2">
            <img src="/image.png" alt="Kuriyam Logo" className="h-9 w-9 object-contain" />
            <CardTitle className="text-2xl font-bold text-teal-700">Kuriyam Code Review</CardTitle>
          </div>
          <CardDescription className="text-center">Admin Panel Login</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Input id="email" name="email" type="email" placeholder="admin@example.com" required className="pl-10" value={email} onChange={e => setEmail(e.target.value)} />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>
            </div>
            <div className="space-y-2 relative">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input id="password" name="password" type={showPassword ? "text" : "password"} placeholder="Enter your password" required className="pl-10 pr-10" value={password} onChange={e => setPassword(e.target.value)} />
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-teal-700 hover:underline" onClick={() => setShowPassword(v => !v)} tabIndex={-1}>
                  {showPassword ? <EyeOff className="h-5 w-5 text-teal-700" /> : <Eye className="h-5 w-5 text-teal-700" />}
                </button>
              </div>
            </div>
            <Button type="submit" className="w-full flex items-center justify-center gap-2" disabled={isLoading}>
              <Shield className="h-5 w-5 text-teal-700" />
              {isLoading ? "Logging in..." : "Login"}
            </Button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Not an admin?{' '}
              <Link href="/" className="text-primary hover:underline">
                Back to User Login
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}