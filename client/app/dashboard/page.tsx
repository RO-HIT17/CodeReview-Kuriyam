"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Github, GitBranch, Plus, Settings, LogOut, ExternalLink } from "lucide-react"
import Link from "next/link"
import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import type { Repository } from "@/lib/definitions"
import {withAuth} from "@/app/hoc/withAuth"

function DashboardPage() {
  const searchParams = useSearchParams()
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)

  async function getIntegratedRepositories(): Promise<Repository[]> {
    const installationId = localStorage.getItem('github_installation_id')
    
    let allRepos: Repository[] = []

    if (installationId) {
      try {
        const token = localStorage.getItem('token') 
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/github/formatted-repos?installation_id=${installationId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        const githubRepos = await response.json()
        allRepos = [...allRepos, ...githubRepos]
      } catch (error) {
        console.error('Error fetching GitHub repositories:', error)
      }
    }

    try {
      const token = localStorage.getItem('token') 
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/bitbucket/workspaces`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const bitbucketData = await response.json()
        console.log('Bitbucket API response:', bitbucketData)
        
        if (bitbucketData.data && Array.isArray(bitbucketData.data) && bitbucketData.data.length > 0) {
          const bitbucketRepos = bitbucketData.data.map((workspace: any) => ({
            id: workspace.workspaceUuid || workspace.clientKey,
            name: workspace.workspaceName || 'Bitbucket Workspace',
            description: `Bitbucket workspace: ${workspace.workspaceName || 'Unknown'}`,
            provider: "bitbucket",
            private: true,
            url: workspace.baseApiUrl || '#',
            language: "Unknown",
            stars: 0,
            forks: 0,
          }))
          allRepos = [...allRepos, ...bitbucketRepos]
        }
      }
    } catch (error) {
      console.error('Error fetching Bitbucket repositories:', error)
    }

    return allRepos
  }

  const name = localStorage.getItem("name")

  useEffect(() => {
    const installationId = searchParams.get('installation_id')
    const code = searchParams.get('code')
    
    if (installationId) {
      localStorage.setItem('github_installation_id', installationId)
      console.log('GitHub installation ID stored:', installationId)
      
      const url = new URL(window.location.href)
      url.searchParams.delete('installation_id')
      url.searchParams.delete('code')
      url.searchParams.delete('setup_action')
      window.history.replaceState({}, document.title, url.pathname)
    }

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
  };

  const handleGitHubConnect = () => {
    const githubUrl = "https://github.com/apps/KuriyamCodeReview/installations/new"
    const popup = window.open(
      githubUrl,
      'github-install',
      'width=600,height=700,scrollbars=yes,resizable=yes'
    )
    
    const checkClosed = setInterval(() => {
      if (popup?.closed) {
        clearInterval(checkClosed)
        getIntegratedRepositories().then((repos) => {
          setRepositories(repos)
        })
      }
    }, 1000)
  }

  const handleBitbucketConnect = () => {
    window.open("https://bitbucket.org/site/addons/authorize?addon_key=code-review-bot", "_blank")
    
    const pollForBitbucketRepos = setInterval(async () => {
      try {
        const token = localStorage.getItem('token')
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/bitbucket/workspaces`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const bitbucketData = await response.json()
          console.log('Polling - Bitbucket data:', bitbucketData)
          
          if (bitbucketData.data && Array.isArray(bitbucketData.data) && bitbucketData.data.length > 0) {
            clearInterval(pollForBitbucketRepos)
            console.log('Bitbucket installation detected, refreshing repos...')
            getIntegratedRepositories().then((repos) => {
              setRepositories(repos)
              console.log('Updated repositories:', repos)
            })
          }
        }
      } catch (error) {
        console.error('Error polling for Bitbucket repos:', error)
      }
    }, 10000)
    
    setTimeout(() => {
      clearInterval(pollForBitbucketRepos)
      console.log('Stopped polling for Bitbucket repos')
    }, 120000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-100 to-gray-200">
      {/* Header */}
      <header className="bg-white border-b border-teal-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <img src="/image.png" alt="Kuriyam Logo" className="h-9 w-9 object-contain" />
              <h1 className="text-2xl font-bold text-teal-700">Kuriyam Code Review</h1>
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
            <Card className="bg-white border border-teal-200 shadow-[0_4px_24px_0_rgba(20,184,166,0.08)]">
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
            <Card className="bg-white border border-teal-200 shadow-[0_4px_24px_0_rgba(20,184,166,0.08)]">
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

export default withAuth(DashboardPage);