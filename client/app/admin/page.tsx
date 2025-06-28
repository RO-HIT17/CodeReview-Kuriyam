"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

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
    setData((prev) => prev.map((item) => item.id === id ? { ...item, approved: true } : item));
    // TODO: Send approve API call
  };
  const handleReject = (id: string) => {
    setData((prev) => prev.map((item) => item.id === id ? { ...item, approved: false, rejected: true } : item));
    // TODO: Send reject API call
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Feedback Admin Panel</h1>
      <div className="overflow-x-auto">
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
              <TableRow key={item.id}>
                <TableCell>{item.timestamp}</TableCell>
                <TableCell>{item.pr}</TableCell>
                <TableCell>{item.issue}</TableCell>
                <TableCell>{item.vote || "None"}</TableCell>
                <TableCell>{item.ip || "None"}</TableCell>
                <TableCell className="capitalize">{item.source}</TableCell>
                <TableCell>{item.repo}</TableCell>
                <TableCell>
                  {item.approved ? (
                    <span className="text-green-600 font-semibold">Approved</span>
                  ) : item.rejected ? (
                    <span className="text-red-600 font-semibold">Rejected</span>
                  ) : (
                    <span className="text-orange-600 font-semibold">Pending</span>
                  )}
                </TableCell>
                <TableCell>
                  {!item.approved && !item.rejected && (
                    <>
                      <Button size="sm" onClick={() => handleApprove(item.id)} className="mr-2">Approve</Button>
                      <Button size="sm" variant="destructive" onClick={() => handleReject(item.id)}>Reject</Button>
                    </>
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
    </div>
  );
} 