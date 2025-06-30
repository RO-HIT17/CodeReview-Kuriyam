"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Github, GitBranch, Plus, Settings, LogOut, ExternalLink } from "lucide-react"
import Link from "next/link"
import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import type { Repository } from "@/lib/definitions"

export default function DashboardPage() {
  const searchParams = useSearchParams()
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)

  async function getIntegratedRepositories(): Promise<Repository[]> {
    const installationId = localStorage.getItem('github_installation_id')
    
    if (!installationId) {
      return []
    }

    try {
      const response = await fetch(`http://localhost:8000/github/formatted-repos?installation_id=${installationId}`)
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error fetching repositories:', error)
      return []
    }
  }

  const name = localStorage.getItem("name")

  useEffect(() => {
    // Extract installation_id from URL parameters
    const installationId = searchParams.get('installation_id')
    const code = searchParams.get('code')
    
    if (installationId) {
      localStorage.setItem('github_installation_id', installationId)
      console.log('GitHub installation ID stored:', installationId)
      
      // Optional: Clean up URL
      const url = new URL(window.location.href)
      url.searchParams.delete('installation_id')
      url.searchParams.delete('code')
      url.searchParams.delete('setup_action')
      window.history.replaceState({}, document.title, url.pathname)
    }

    // Fetch repositories after installation_id is set
    getIntegratedRepositories().then((repos) => {
      setRepositories(repos)
      setLoading(false)
    })
  }, [searchParams])

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("name");
    localStorage.removeItem("user_id");
    localStorage.removeItem("github_installation_id");
    // Redirect will happen via the Link
  };

  const handleGitHubConnect = () => {
    const githubUrl = "https://github.com/apps/KuriyamCodeReview/installations/new"
    const popup = window.open(
      githubUrl,
      'github-install',
      'width=600,height=700,scrollbars=yes,resizable=yes'
    )
    
    // Optional: Listen for popup close or message
    const checkClosed = setInterval(() => {
      if (popup?.closed) {
        clearInterval(checkClosed)
        // Refresh repositories after installation
        getIntegratedRepositories().then((repos) => {
          setRepositories(repos)
        })
      }
    }, 1000)
  }

  const handleBitbucketConnect = () => {
    // For now, just show an alert or implement your bitbucket logic
    alert("Bitbucket integration coming soon!")
  }

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
                <Button variant="outline" className="w-full justify-start" onClick={handleGitHubConnect}>
                  <Github className="h-4 w-4 mr-2" />
                  Connect GitHub
                  <ExternalLink className="h-4 w-4 ml-auto" />
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={handleBitbucketConnect}>
                  <GitBranch className="h-4 w-4 mr-2" />
                  Connect Bitbucket
                  <ExternalLink className="h-4 w-4 ml-auto" />
                </Button>
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
                {loading ? (
                  <div className="text-center py-12">
                    <p>Loading repositories...</p>
                  </div>
                ) : repositories.length > 0 ? (
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
