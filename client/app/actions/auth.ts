"use server"

import { redirect } from "next/navigation"
import { cookies } from "next/headers"
import { SignupFormSchema, type FormState } from "@/lib/definitions"
import { createSession } from "@/lib/auth"

export async function signup(state: FormState, formData: FormData): Promise<FormState> {
  // Validate form fields
  const validatedFields = SignupFormSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    password: formData.get("password"),
    confirmPassword: formData.get("confirmPassword"),
  })

  // If any form fields are invalid, return early
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    }
  }

  const { name, email, password } = validatedFields.data

  // In a real application, you would:
  // 1. Hash the password
  // 2. Check if user already exists
  // 3. Insert user into database

  // For demo purposes, simulate user creation
  const user = {
    id: Math.random().toString(36).substr(2, 9),
    name,
    email,
  }

  // Create session
  await createSession(user.id, user)

  redirect("/dashboard")
}

export async function login(formData: FormData) {
  const email = formData.get("email") as string
  const password = formData.get("password") as string

  // In a real application, you would:
  // 1. Verify credentials against database
  // 2. Handle authentication errors

  // For demo purposes, simulate successful login
  if (email && password) {
    const user = {
      id: "demo-user-id",
      name: "Demo User",
      email,
    }

    await createSession(user.id, user)
    redirect("/dashboard")
  }

  redirect("/?error=invalid_credentials")
}

export async function logout() {
  const cookieStore = await cookies()
  cookieStore.delete("session")
  redirect("/")
}
