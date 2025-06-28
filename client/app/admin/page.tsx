"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Clock } from "lucide-react";
import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from "@/components/ui/navigation-menu";

// Placeholder fetch function (replace with real API call)
async function fetchFeedback() {
  // Simulate API call
  return [
    {
      id: "d96ee7c4-7352-405f-b286-0ff58764a551",
      timestamp: "2025-06-24T22:58:21.531732",
      pr: 53,
      issue: "52",
      vote: null,
      ip: null,
      source: "github",
      repo: "octocat/Hello-World",
      repoUrl: "https://github.com/octocat/Hello-World",
      approved: false,
    },
    {
      id: "584b2fa2-7d80-42ad-a9be-ff1755e73799",
      timestamp: "2025-06-24T23:10:20.788226",
      pr: 55,
      issue: "54",
      vote: null,
      ip: null,
      source: "bitbucket",
      repo: "team/repo",
      repoUrl: "https://bitbucket.org/team/repo",
      approved: false,
    },
  ];
}

export default function AdminPanel() {
  const router = useRouter();
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined" && localStorage.getItem("isAdmin") !== "true") {
      router.push("/admin/login");
    } else {
      fetchFeedback().then((d) => {
        setData(d);
        setLoading(false);
      });
    }
  }, [router]);

  const handleApprove = (id: string) => {
    setData((prev) => prev.map((item) => item.id === id ? { ...item, approved: true, rejected: false } : item));
    setActionMsg("Approved successfully.");
    setTimeout(() => setActionMsg(""), 2000);
    // TODO: Send approve API call
  };
  const handleReject = (id: string) => {
    setData((prev) => prev.map((item) => item.id === id ? { ...item, approved: false, rejected: true } : item));
    setActionMsg("Rejected successfully.");
    setTimeout(() => setActionMsg(""), 2000);
    // TODO: Send reject API call
  };

  if (loading) return <div className="p-8">Loading...</div>;

  const handleLogout = () => {
    localStorage.removeItem("isAdmin");
    router.push("/admin/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="sticky top-0 z-20 w-full bg-white border-b shadow-sm mb-8">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
          <span className="font-bold text-lg tracking-tight">Kuriyam Admin</span>
          <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
        </div>
      </nav>
      <div className="flex items-center justify-center py-12 px-4">
        <Card className="w-full max-w-6xl shadow-lg">
          <CardHeader className="flex flex-row items-center gap-4 pb-2">
            <Clock className="text-primary" size={32} />
            <CardTitle className="text-2xl font-bold">Feedback Admin Panel</CardTitle>
          </CardHeader>
          <CardContent>
            {actionMsg && <div className="mb-4 text-center text-green-600 font-semibold">{actionMsg}</div>}
            <div className="overflow-x-auto rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>PR</TableHead>
                    <TableHead>Issue</TableHead>
                    <TableHead>Vote</TableHead>
                    <TableHead>IP</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Repo Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Redirect</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.map((item) => (
                    <TableRow key={item.id} className="hover:bg-muted/30 transition-colors">
                      <TableCell>{item.timestamp}</TableCell>
                      <TableCell>{item.pr}</TableCell>
                      <TableCell>{item.issue}</TableCell>
                      <TableCell>{item.vote || "None"}</TableCell>
                      <TableCell>{item.ip || "None"}</TableCell>
                      <TableCell className="capitalize">{item.source}</TableCell>
                      <TableCell>{item.repo}</TableCell>
                      <TableCell>
                        {item.approved ? (
                          <Badge variant="outline" className="text-green-700 border-green-400 bg-green-50 flex items-center gap-1"><CheckCircle2 size={16}/> Approved</Badge>
                        ) : item.rejected ? (
                          <Badge variant="outline" className="text-red-700 border-red-400 bg-red-50 flex items-center gap-1"><XCircle size={16}/> Rejected</Badge>
                        ) : (
                          <Badge variant="outline" className="text-orange-700 border-orange-400 bg-orange-50 flex items-center gap-1"><Clock size={16}/> Pending</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {!item.approved && !item.rejected && (
                          <div className="flex gap-2">
                            <Button size="sm" onClick={() => handleApprove(item.id)} className="bg-green-600 hover:bg-green-700 text-white">Approve</Button>
                            <Button size="sm" variant="destructive" onClick={() => handleReject(item.id)}>Reject</Button>
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button size="sm" variant="link" onClick={() => window.open(item.repoUrl, "_blank")}>Go to Repo</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 