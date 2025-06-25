import { z } from "zod"

export const SignupFormSchema = z
  .object({
    name: z.string().min(2, { message: "Name must be at least 2 characters long." }).trim(),
    email: z.string().email({ message: "Please enter a valid email." }).trim(),
    password: z
      .string()
      .min(8, { message: "Be at least 8 characters long" })
      .regex(/[a-zA-Z]/, { message: "Contain at least one letter." })
      .regex(/[0-9]/, { message: "Contain at least one number." })
      .regex(/[^a-zA-Z0-9]/, {
        message: "Contain at least one special character.",
      })
      .trim(),
    confirmPassword: z.string().trim(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords must match.",
    path: ["confirmPassword"],
  })

export type FormState =
  | {
      errors?: {
        name?: string[]
        email?: string[]
        password?: string[]
        confirmPassword?: string[]
      }
      message?: string
    }
  | undefined

export interface User {
  id: string
  name: string
  email: string
}

export interface Session {
  userId: string
  user: User
  expiresAt: Date
}

export interface Repository {
  id: string
  name: string
  description: string
  provider: "github" | "bitbucket"
  private: boolean
  url: string
  language?: string
  stars?: number
  forks?: number
}
