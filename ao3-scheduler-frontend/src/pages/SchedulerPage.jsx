import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Select, SelectItem } from "../components/ui/select";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Table, TableHead, TableRow, TableCell, TableBody } from "../components/ui/table";
import { DateTimePicker } from "../components/ui/datetimepicker";
import { Switch } from "../components/ui/switch";

import { useState, useEffect } from "react";

import { useQuery, useMutation } from "@tanstack/react-query";
import axios from "axios";

export default function Scheduler() {
  const [completedOnly, setCompletedOnly] = useState(false);
  const [fics, setFics] = useState([]);
  const [filters, setFilters] = useState({
    title: "",
    fandom: "",
    tags: "",
    sortBy: "posted_at",
    sortOrder: "desc",
  });
  const [newFic, setNewFic] = useState({
    title: "",
    fandom: "",
    content: "",
    scheduled_time: new Date(),
  });

  const { data: fandoms } = useQuery("fandoms", () => axios.get("/api/fandoms").then((res) => res.data));
  const { data: scheduledFics, refetch } = useQuery("scheduledFics", () => axios.get("/api/scheduled").then((res) => res.data));
  const scheduleFicMutation = useMutation((fic) => axios.post("/api/schedule-fic", fic), {
    onSuccess: () => refetch(),
  });

  useEffect(() => {
    if (scheduledFics) {
      setFics(
        scheduledFics.filter((fic) => (completedOnly ? fic.is_complete : true))
      );
    }
  }, [scheduledFics, completedOnly]);

  return (
    <div className="p-4 space-y-6">
      <Card>
        <CardHeader>Schedule a New Fic</CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="Title" value={newFic.title} onChange={(e) => setNewFic({ ...newFic, title: e.target.value })} />
          <Select value={newFic.fandom} onChange={(value) => setNewFic({ ...newFic, fandom: value })}>
            {fandoms?.map((fandom) => (
              <SelectItem key={fandom} value={fandom}>{fandom}</SelectItem>
            ))}
          </Select>
          <Input placeholder="Content" value={newFic.content} onChange={(e) => setNewFic({ ...newFic, content: e.target.value })} />
          <DateTimePicker value={newFic.scheduled_time} onChange={(date) => setNewFic({ ...newFic, scheduled_time: date })} />
          <Button onClick={() => scheduleFicMutation.mutate(newFic)}>Schedule Fic</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>Scheduled Fics</CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <Input placeholder="Filter by title" onChange={(e) => setFilters({ ...filters, title: e.target.value })} />
            <Switch checked={completedOnly} onCheckedChange={setCompletedOnly}>Completed Only</Switch>
          </div>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Fandom</TableCell>
                <TableCell>Scheduled Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {fics.map((fic) => (
                <TableRow key={fic.id}>
                  <TableCell>{fic.title}</TableCell>
                  <TableCell>{fic.fandom}</TableCell>
                  <TableCell>{new Date(fic.scheduled_time).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
