"use client";
import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Clock, ExternalLink, ChevronDown, ChevronUp } from "lucide-react";
import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from "@/components/ui/navigation-menu";
import {withAuth} from "../hoc/withAuth";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationPrevious, PaginationNext } from "@/components/ui/pagination";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";

async function fetchFeedback() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/feedback-list`,{
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem("token")}`,
    }});
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching feedback:', error);
    return [];
  }
}

function AdminPanel() {
  const router = useRouter();
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState("");
  const token = localStorage.getItem("token");
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [platformFilter, setPlatformFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("timestamp");
  const [sortOrder, setSortOrder] = useState("desc");

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

  const handleApprove = async (pr: number, issue: string, timestamp: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/approve-feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ pr, issue, timestamp }),
      });
      
      if (response.ok) {
        setData((prev) => prev.map((item) => 
          item.pr === pr && item.issue === issue && item.timestamp === timestamp 
            ? { ...item, approved: true, rejected: false } 
            : item
        ));
        setActionMsg("Approved successfully.");
        setTimeout(() => setActionMsg(""), 2000);
      }
    } catch (error) {
      console.error('Error approving feedback:', error);
      setActionMsg("Error approving feedback.");
      setTimeout(() => setActionMsg(""), 2000);
    }
  };

  const handleReject = async (pr: number, issue: string, timestamp: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/reject-feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ pr, issue, timestamp }),
      });
      
      if (response.ok) {
        setData((prev) => prev.map((item) => 
          item.pr === pr && item.issue === issue && item.timestamp === timestamp 
            ? { ...item, approved: false, rejected: true } 
            : item
        ));
        setActionMsg("Rejected successfully.");
        setTimeout(() => setActionMsg(""), 2000);
      }
    } catch (error) {
      console.error('Error rejecting feedback:', error);
      setActionMsg("Error rejecting feedback.");
      setTimeout(() => setActionMsg(""), 2000);
    }
  };

  // Filtering
  const filteredData = useMemo(() => {
    return data.filter(item => {
      const platformMatch = platformFilter === "all" || (item.platform && item.platform.toLowerCase() === platformFilter);
      const statusMatch = statusFilter === "all" || (statusFilter === "approved" && item.approved) || (statusFilter === "rejected" && item.rejected) || (statusFilter === "pending" && !item.approved && !item.rejected);
      return platformMatch && statusMatch;
    });
  }, [data, platformFilter, statusFilter]);

  // Sorting
  const sortedData = useMemo(() => {
    return [...filteredData].sort((a, b) => {
      if (sortBy === "status") {
        // Approved > Pending > Rejected (desc)
        const getStatusRank = (item: any) => item.approved ? 2 : item.rejected ? 0 : 1;
        const rankA = getStatusRank(a);
        const rankB = getStatusRank(b);
        if (rankA < rankB) return sortOrder === "asc" ? -1 : 1;
        if (rankA > rankB) return sortOrder === "asc" ? 1 : -1;
        return 0;
      }
      let valA = a[sortBy];
      let valB = b[sortBy];
      if (sortBy === "timestamp") {
        valA = new Date(valA);
        valB = new Date(valB);
      }
      if (valA < valB) return sortOrder === "asc" ? -1 : 1;
      if (valA > valB) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortBy, sortOrder]);

  // Pagination
  const totalRows = sortedData.length;
  const totalPages = Math.ceil(totalRows / rowsPerPage);
  const paginatedData = sortedData.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

  if (loading) return <div className="p-8">Loading...</div>;

  const handleLogout = () => {
    localStorage.removeItem("isAdmin");
    localStorage.removeItem("token");
    localStorage.removeItem("name");
    localStorage.removeItem("user_id");
    router.push("/admin/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-100 to-gray-200">
      <nav className="sticky top-0 z-20 w-full bg-white border-b border-teal-200 shadow-sm mb-8">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <img src="/image.png" alt="Kuriyam Logo" className="h-8 w-8 object-contain" />
            <span className="font-bold text-lg tracking-tight text-teal-700">Kuriyam Admin</span>
          </div>
          <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
        </div>
      </nav>
      <div className="flex items-center justify-center py-12 px-4">
        <Card className="w-full max-w-7xl bg-white border border-teal-100 shadow-lg rounded-2xl px-10 py-10">
          <CardHeader className="pb-4">
            <CardTitle className="text-3xl font-bold text-teal-700 mb-2">Feedback Admin Panel</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Control Bar */}
            <div className="flex flex-wrap gap-4 items-center justify-between mb-6">
              <div className="flex gap-4 items-center flex-wrap">
                <span className="font-medium text-sm">Rows per page:</span>
                <Select value={rowsPerPage.toString()} onValueChange={v => { setRowsPerPage(Number(v)); setCurrentPage(1); }}>
                  <SelectTrigger className="w-20 h-9 text-sm rounded-md" >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[10, 20, 50, 100].map(n => <SelectItem key={n} value={n.toString()}>{n}</SelectItem>)}
                  </SelectContent>
                </Select>
                <span className="font-medium text-sm">Platform:</span>
                <Select value={platformFilter} onValueChange={v => { setPlatformFilter(v); setCurrentPage(1); }}>
                  <SelectTrigger className="w-28 h-9 text-sm rounded-md">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="github">GitHub</SelectItem>
                    <SelectItem value="bitbucket">Bitbucket</SelectItem>
                  </SelectContent>
                </Select>
                <span className="font-medium text-sm">Status:</span>
                <Select value={statusFilter} onValueChange={v => { setStatusFilter(v); setCurrentPage(1); }}>
                  <SelectTrigger className="w-28 h-9 text-sm rounded-md">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                  </SelectContent>
                </Select>
                <span className="font-medium text-sm">Sort by:</span>
                <div className="flex items-center gap-1">
                  <Select value={sortBy} onValueChange={v => setSortBy(v)}>
                    <SelectTrigger className="w-32 h-9 text-sm rounded-md">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="timestamp">Timestamp</SelectItem>
                      <SelectItem value="pr">PR</SelectItem>
                      <SelectItem value="status">Status</SelectItem>
                    </SelectContent>
                  </Select>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-9 w-9" onClick={() => setSortOrder(o => o === "asc" ? "desc" : "asc")}>{sortOrder === "asc" ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}</Button>
                      </TooltipTrigger>
                      <TooltipContent>{`Sort order: ${sortOrder === "asc" ? "Ascending" : "Descending"}`}</TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            </div>
            {/* Table */}
            <div className="overflow-x-auto rounded-lg border border-teal-50">
              <Table>
                <TableHeader className="sticky top-0 bg-white z-10">
                  <TableRow>
                    <TableHead className="py-4 px-3 text-base font-semibold">Timestamp</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">PR</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Issue</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Vote</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">IP</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Source</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Repo Name</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Status</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Action</TableHead>
                    <TableHead className="py-4 px-3 text-base font-semibold">Redirect</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedData.map((item) => (
                    <TableRow key={item.id} className="hover:bg-teal-50/60 transition-colors rounded-lg">
                      <TableCell className="py-3 px-3">{item.timestamp}</TableCell>
                      <TableCell className="py-3 px-3">{item.pr}</TableCell>
                      <TableCell className="py-3 px-3">{item.issue}</TableCell>
                      <TableCell className="py-3 px-3">{item.vote || "None"}</TableCell>
                      <TableCell className="py-3 px-3">{item.ip || "None"}</TableCell>
                      <TableCell className="py-3 px-3 capitalize">{item.platform}</TableCell>
                      <TableCell className="py-3 px-3">{item.repo}</TableCell>
                      <TableCell className="py-3 px-3">
                        {item.approved ? (
                          <Badge variant="outline" className="text-green-700 border-green-200 bg-green-50 flex items-center gap-1 px-2 py-1 rounded-full"><CheckCircle2 size={16}/> Approved</Badge>
                        ) : item.rejected ? (
                          <Badge variant="outline" className="text-red-700 border-red-200 bg-red-50 flex items-center gap-1 px-2 py-1 rounded-full"><XCircle size={16}/> Rejected</Badge>
                        ) : (
                          <Badge variant="outline" className="text-orange-700 border-orange-200 bg-orange-50 flex items-center gap-1 px-2 py-1 rounded-full"><Clock size={16}/> Pending</Badge>
                        )}
                      </TableCell>
                      <TableCell className="py-3 px-3">
                        {!item.approved && !item.rejected && (
                          <div className="flex gap-2">
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button size="icon" className="rounded-full bg-green-600 hover:bg-green-700 text-white shadow-sm" onClick={() => handleApprove(item.pr, item.issue, item.timestamp)}>
                                    <CheckCircle2 className="h-6 w-6" />
                                    <span className="sr-only">Approve</span>
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Approve</TooltipContent>
                              </Tooltip>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button size="icon" className="rounded-full bg-red-500 hover:bg-red-600 text-white shadow-sm" variant="destructive" onClick={() => handleReject(item.pr, item.issue, item.timestamp)}>
                                    <XCircle className="h-6 w-6" />
                                    <span className="sr-only">Reject</span>
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Reject</TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="py-3 px-3">
                        <Button size="icon" variant="ghost" className="text-teal-700 hover:bg-teal-50 rounded-full" onClick={() => window.open(item.redirect, "_blank")}> 
                          <ExternalLink className="h-5 w-5" />
                          <span className="sr-only">Go to Repo</span>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            {/* Pagination */}
            <div className="flex justify-between items-center mt-6">
              <div className="text-sm text-muted-foreground">{`Page ${currentPage} of ${totalPages} (${totalRows} rows)`}</div>
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious href="#" onClick={e => { e.preventDefault(); setCurrentPage(p => Math.max(1, p - 1)); }} />
                  </PaginationItem>
                  {[...Array(totalPages)].map((_, i) => (
                    <PaginationItem key={i}>
                      <PaginationLink href="#" isActive={currentPage === i + 1} onClick={e => { e.preventDefault(); setCurrentPage(i + 1); }}>{i + 1}</PaginationLink>
                    </PaginationItem>
                  ))}
                  <PaginationItem>
                    <PaginationNext href="#" onClick={e => { e.preventDefault(); setCurrentPage(p => Math.min(totalPages, p + 1)); }} />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default withAuth(AdminPanel);