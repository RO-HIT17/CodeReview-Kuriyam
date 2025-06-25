import { cookies } from "next/headers"
import type { User, Session, Repository } from "./definitions"

// In a real application, you would use a proper session management library
// and store sessions in a database or secure cookie with encryption

export async function createSession(userId: string, user: User) {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
  const session: Session = {
    userId,
    user,
    expiresAt,
  }

  const cookieStore = await cookies()
  cookieStore.set("session", JSON.stringify(session), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    expires: expiresAt,
    sameSite: "lax",
    path: "/",
  })
}

export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies()
  const sessionCookie = cookieStore.get("session")

  if (!sessionCookie) {
    return null
  }

  try {
    const session: Session = JSON.parse(sessionCookie.value)

    // Check if session is expired
    if (new Date(session.expiresAt) < new Date()) {
      return null
    }

    return session
  } catch {
    return null
  }
}

export async function verifySession(): Promise<Session | null> {
  return await getSession()
}

export async function deleteSession() {
  const cookieStore = await cookies()
  cookieStore.delete("session")
}

// Mock function to get integrated repositories
export async function getIntegratedRepositories(userId: string): Promise<Repository[]> {
  // In a real application, this would query your database
  // For demo purposes, return mock data
  return [
    {
      id: "1",
      name: "my-awesome-app",
      description: "A full-stack web application built with Next.js",
      provider: "github",
      private: false,
      url: "https://github.com/user/my-awesome-app",
      language: "TypeScript",
      stars: 25,
      forks: 8,
    },
    {
      id: "2",
      name: "secret-project",
      description: "Private repository for internal tools",
      provider: "bitbucket",
      private: true,
      url: "https://bitbucket.org/user/secret-project",
      language: "Python",
      stars: 0,
      forks: 0,
    },
  ]
}
