import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"

export async function GET(request: NextRequest) {
  const session = await getSession()

  if (!session) {
    return NextResponse.redirect(new URL("/", request.url))
  }

  // In a real application, you would:
  // 1. Generate a state parameter for security
  // 2. Redirect to GitHub OAuth URL
  // const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${process.env.GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(process.env.GITHUB_REDIRECT_URI)}&scope=repo&state=${state}`

  // For demo purposes, simulate OAuth flow by redirecting to callback
  const callbackUrl = new URL("/auth/callback", request.url)
  callbackUrl.searchParams.set("provider", "github")
  callbackUrl.searchParams.set("code", "mock_auth_code")

  return NextResponse.redirect(callbackUrl)
}
