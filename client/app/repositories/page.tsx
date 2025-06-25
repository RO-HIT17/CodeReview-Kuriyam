"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Github, GitBranch, ArrowLeft, Check } from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

// Mock repository data - in real app, this would come from OAuth callback
const mockRepositories = [
  {
    id: 1,
    name: "awesome-project",
    description: "A really awesome project with lots of features",
    private: false,
    language: "TypeScript",
    stars: 42,
    forks: 12,
  },
  {
    id: 2,
    name: "secret-sauce",
    description: "Private repository with proprietary code",
    private: true,
    language: "Python",
    stars: 0,
    forks: 0,
  },
  {
    id: 3,
    name: "web-components",
    description: "Reusable web components library",
    private: false,
    language: "JavaScript",
    stars: 128,
    forks: 34,
  },
  {
    id: 4,
    name: "data-pipeline",
    description: "ETL pipeline for processing large datasets",
    private: true,
    language: "Python",
    stars: 0,
    forks: 0,
  },
]

export default function RepositoriesPage() {
  const searchParams = useSearchParams()
  const provider = searchParams.get("provider") || "github"
  const [selectedRepos, setSelectedRepos] = useState<number[]>([])
  const [isIntegrating, setIsIntegrating] = useState(false)

  const handleRepoToggle = (repoId: number) => {
    setSelectedRepos((prev) => (prev.includes(repoId) ? prev.filter((id) => id !== repoId) : [...prev, repoId]))
  }

  const handleIntegrate = async () => {
    setIsIntegrating(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setIsIntegrating(false)
    // Redirect to dashboard
    window.location.href = "/dashboard"
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="mr-4">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              {provider === "github" ? <Github className="h-6 w-6" /> : <GitBranch className="h-6 w-6" />}
              <h1 className="text-xl font-semibold capitalize">Select {provider} Repositories</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Choose repositories to integrate</CardTitle>
            <CardDescription>
              Select the repositories you want to manage through this application. You can change this selection later
              in your settings.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockRepositories.map((repo) => (
                <div key={repo.id} className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-gray-50">
                  <Checkbox
                    id={`repo-${repo.id}`}
                    checked={selectedRepos.includes(repo.id)}
                    onCheckedChange={() => handleRepoToggle(repo.id)}
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="font-medium">{repo.name}</h3>
                      <Badge variant={repo.private ? "secondary" : "outline"}>
                        {repo.private ? "Private" : "Public"}
                      </Badge>
                      {repo.language && (
                        <Badge variant="outline" className="text-xs">
                          {repo.language}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{repo.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <span>★ {repo.stars}</span>
                      <span>⑂ {repo.forks}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between mt-8 pt-6 border-t">
              <p className="text-sm text-muted-foreground">
                {selectedRepos.length} of {mockRepositories.length} repositories selected
              </p>
              <div className="flex space-x-3">
                <Link href="/dashboard">
                  <Button variant="outline">Skip for now</Button>
                </Link>
                <Button onClick={handleIntegrate} disabled={selectedRepos.length === 0 || isIntegrating}>
                  {isIntegrating ? (
                    "Integrating..."
                  ) : (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Integrate Selected ({selectedRepos.length})
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
