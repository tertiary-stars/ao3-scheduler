import { useState, useEffect } from "react";
import axios from "axios";
import { useQuery, useMutation } from "react-query";

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
      <div className="bg-white p-6 rounded-xl shadow">
        <h2 className="text-xl font-bold mb-4">Schedule a New Fic</h2>
        <input
          type="text"
          placeholder="Title"
          value={newFic.title}
          onChange={(e) => setNewFic({ ...newFic, title: e.target.value })}
          className="w-full p-2 border rounded mb-2"
        />
        <select
          value={newFic.fandom}
          onChange={(e) => setNewFic({ ...newFic, fandom: e.target.value })}
          className="w-full p-2 border rounded mb-2"
        >
          {fandoms?.map((fandom) => (
            <option key={fandom} value={fandom}>
              {fandom}
            </option>
          ))}
        </select>
        <textarea
          placeholder="Content"
          value={newFic.content}
          onChange={(e) => setNewFic({ ...newFic, content: e.target.value })}
          className="w-full p-2 border rounded mb-2"
        />
        <input
          type="datetime-local"
          value={newFic.scheduled_time}
          onChange={(e) => setNewFic({ ...newFic, scheduled_time: e.target.value })}
          className="w-full p-2 border rounded mb-2"
        />
        <button
          onClick={() => scheduleFicMutation.mutate(newFic)}
          className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Schedule Fic
        </button>
      </div>

      <div className="bg-white p-6 rounded-xl shadow">
        <h2 className="text-xl font-bold mb-4">Scheduled Fics</h2>
        <div className="flex justify-between mb-4">
          <input
            type="text"
            placeholder="Filter by title"
            onChange={(e) => setFilters({ ...filters, title: e.target.value })}
            className="p-2 border rounded"
          />
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={completedOnly}
              onChange={(e) => setCompletedOnly(e.target.checked)}
              className="mr-2"
            />
            Completed Only
          </label>
        </div>
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">Title</th>
              <th className="border p-2">Fandom</th>
              <th className="border p-2">Scheduled Time</th>
            </tr>
          </thead>
          <tbody>
            {fics.map((fic) => (
              <tr key={fic.id} className="text-center">
                <td className="border p-2">{fic.title}</td>
                <td className="border p-2">{fic.fandom}</td>
                <td className="border p-2">{new Date(fic.scheduled_time).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
