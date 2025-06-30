"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Github, GitBranch, Plus, Settings, LogOut, ExternalLink } from "lucide-react"
import Link from "next/link"
import type { Repository } from "@/lib/definitions"
export default async function DashboardPage() {
  
  async function getIntegratedRepositories(userId: string): Promise<Repository[]> {
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
  

  const repositories = await getIntegratedRepositories("1")
  const name = localStorage.getItem("name")

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("name");
    // Redirect will happen via the Link
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <GitBranch className="h-6 w-6" />
              <h1 className="text-xl font-semibold">Kuriyam - Code Reviewer</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">Welcome, {name}</span>
                <Link href="/">
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
                </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Repository Integration */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Plus className="h-5 w-5" />
                  <span>Connect Repositories</span>
                </CardTitle>
                <CardDescription>Link your external repository accounts to manage them here</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Link href="https://github.com/apps/KuriyamCodeReview/installations/new">
                  <Button variant="outline" className="w-full justify-start">
                    <Github className="h-4 w-4 mr-2" />
                    Connect GitHub
                    <ExternalLink className="h-4 w-4 ml-auto" />
                  </Button>
                </Link>
                <Link href="https://bitbucket.org/site/addons/authorize?addon_key=code-review-bot">
                  <Button variant="outline" className="w-full justify-start">
                    <GitBranch className="h-4 w-4 mr-2" />
                    Connect Bitbucket
                    <ExternalLink className="h-4 w-4 ml-auto" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>

          {/* Integrated Repositories */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Your Repositories</CardTitle>
                <CardDescription>
                  {repositories.length > 0
                    ? `Manage your ${repositories.length} integrated repositories`
                    : "No repositories connected yet. Connect your accounts to get started."}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {repositories.length > 0 ? (
                  <div className="space-y-4">
                    {repositories.map((repo) => (
                      <div key={repo.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          {repo.provider === "github" ? (
                            <Github className="h-5 w-5" />
                          ) : (
                            <GitBranch className="h-5 w-5" />
                          )}
                          <div>
                            <h3 className="font-medium">{repo.name}</h3>
                            <p className="text-sm text-muted-foreground">{repo.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={repo.private ? "secondary" : "outline"}>
                            {repo.private ? "Private" : "Public"}
                          </Badge>
                          <Badge variant="outline" className="capitalize">
                            {repo.provider}
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <GitBranch className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium mb-2">No repositories yet</h3>
                    <p className="text-muted-foreground mb-4">
                      Connect your GitHub or Bitbucket account to start managing repositories
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
