import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { getUsers, updateUserRole } from "../../api/users";
import LoadingSpinner from "../../components/LoadingSpinner";
import StatusBadge from "../../components/StatusBadge";
import { UserRole } from "../../types";

const roles: UserRole[] = ["student", "staff", "equipment_manager", "admin"];

export default function UserManager() {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const usersQuery = useQuery({
    queryKey: ["users"],
    queryFn: getUsers
  });

  const roleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      updateUserRole(userId, role),
    onSuccess: (user) => {
      setError("");
      setMessage(`${user.email} is now ${user.role}.`);
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (err: any) => {
      setMessage("");
      setError(err.response?.data?.detail ?? "Could not update user role.");
    }
  });

  if (usersQuery.isLoading) {
    return <LoadingSpinner label="Loading users" />;
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-ink">Users</h1>
        <p className="mt-1 text-sm text-slate-600">
          Change local application roles used by backend permissions.
        </p>
      </div>

      {message && <p className="rounded bg-green-50 px-4 py-3 text-sm text-green-800">{message}</p>}
      {error && <p className="rounded bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      <section className="rounded-lg border border-line bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-line text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Current role</th>
                <th className="px-4 py-3">Change role</th>
                <th className="px-4 py-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {usersQuery.data?.map((user) => (
                <tr key={user.id}>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-ink">{user.full_name}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={user.role} />
                  </td>
                  <td className="px-4 py-3">
                    <select
                      className="form-input w-52"
                      value={user.role}
                      disabled={roleMutation.isPending}
                      onChange={(event) =>
                        roleMutation.mutate({
                          userId: user.id,
                          role: event.target.value as UserRole
                        })
                      }
                    >
                      {roles.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : "Unknown"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
