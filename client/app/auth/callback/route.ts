import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const provider = searchParams.get("provider")
  const code = searchParams.get("code")
  const error = searchParams.get("error")

  const session = await getSession()

  if (!session) {
    return NextResponse.redirect(new URL("/", request.url))
  }

  if (error) {
    // Handle OAuth error
    const dashboardUrl = new URL("/dashboard", request.url)
    dashboardUrl.searchParams.set("error", "oauth_failed")
    return NextResponse.redirect(dashboardUrl)
  }

  if (!code || !provider) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  // In a real application, you would:
  // 1. Exchange the code for an access token
  // 2. Use the access token to fetch user's repositories
  // 3. Store the integration in your database

  // For demo purposes, redirect to repository selection
  const repoUrl = new URL("/repositories", request.url)
  repoUrl.searchParams.set("provider", provider)

  return NextResponse.redirect(repoUrl)
}
