import { useQuery } from "@tanstack/react-query";

import { getNotifications } from "../api/notifications";
import LoadingSpinner from "../components/LoadingSpinner";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export default function Notifications() {
  const notificationsQuery = useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications
  });

  if (notificationsQuery.isLoading) {
    return <LoadingSpinner label="Loading notifications" />;
  }

  const notifications = notificationsQuery.data ?? [];

  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-ink">Notifications</h1>
        <p className="mt-1 text-sm text-slate-600">
          Return reminders and system messages sent to your account.
        </p>
      </div>

      <div className="overflow-hidden rounded border border-line bg-white">
        <table className="min-w-full divide-y divide-line text-sm">
          <thead className="bg-slate-50 text-left text-xs font-bold uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Message</th>
              <th className="px-4 py-3">Sent</th>
              <th className="px-4 py-3">Reservation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {notifications.map((notification) => (
              <tr key={notification.id}>
                <td className="whitespace-nowrap px-4 py-3 font-semibold uppercase text-sky-800">
                  {notification.type}
                </td>
                <td className="px-4 py-3 text-slate-700">{notification.message}</td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {formatDate(notification.sent_at)}
                </td>
                <td className="max-w-[12rem] truncate px-4 py-3 font-mono text-xs text-slate-500">
                  {notification.reservation_id}
                </td>
              </tr>
            ))}

            {!notifications.length && (
              <tr>
                <td className="px-4 py-8 text-center text-slate-500" colSpan={4}>
                  No notifications yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
