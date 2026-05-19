import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import {
  createEquipment,
  deleteEquipment,
  EquipmentPayload,
  getEquipment,
  updateEquipment,
  updateEquipmentStatus
} from "../../api/equipment";
import LoadingSpinner from "../../components/LoadingSpinner";
import StatusBadge from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";
import { Equipment, EquipmentStatus } from "../../types";

const statuses: EquipmentStatus[] = [
  "available",
  "reserved",
  "borrowed",
  "serviced",
  "damaged"
];

const emptyDefaults: EquipmentPayload = {
  name: "",
  type: "laptop",
  serial_number: "",
  technical_spec: "",
  location: "",
  max_rental_days: 7,
  image_url: ""
};

export default function EquipmentManager() {
  const { isRole } = useAuth();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<Equipment | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [error, setError] = useState("");

  const equipmentQuery = useQuery({
    queryKey: ["equipment", "admin"],
    queryFn: () => getEquipment()
  });

  const formDefaults = useMemo<EquipmentPayload>(
    () =>
      editing
        ? {
            name: editing.name,
            type: editing.type,
            serial_number: editing.serial_number,
            technical_spec: editing.technical_spec ?? "",
            location: editing.location ?? "",
            max_rental_days: editing.max_rental_days,
            image_url: editing.image_url ?? ""
          }
        : emptyDefaults,
    [editing]
  );

  function closeForm() {
    setEditing(null);
    setIsFormOpen(false);
    setError("");
  }

  const saveMutation = useMutation({
    mutationFn: (payload: EquipmentPayload) =>
      editing ? updateEquipment(editing.id, payload) : createEquipment(payload),
    onSuccess: () => {
      closeForm();
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
    },
    onError: (err: any) => setError(err.response?.data?.detail ?? "Could not save equipment.")
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEquipment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["equipment"] }),
    onError: (err: any) => setError(err.response?.data?.detail ?? "Could not delete equipment.")
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: EquipmentStatus }) =>
      updateEquipmentStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["equipment"] }),
    onError: (err: any) => setError(err.response?.data?.detail ?? "Could not change status.")
  });

  if (equipmentQuery.isLoading) {
    return <LoadingSpinner label="Loading equipment manager" />;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold text-ink">Equipment Manager</h1>
          <p className="mt-1 text-sm text-slate-600">
            Add, edit, delete, and change equipment status.
          </p>
        </div>
        <button
          className="btn-primary"
          onClick={() => {
            setEditing(null);
            setIsFormOpen(true);
          }}
        >
          Add Equipment
        </button>
      </div>

      {error && <p className="rounded bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      {isFormOpen && (
        <EquipmentForm
          defaults={formDefaults}
          isSubmitting={saveMutation.isPending}
          onCancel={closeForm}
          onSubmit={(payload) => saveMutation.mutate(payload)}
        />
      )}

      <section className="rounded-lg border border-line bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-line text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Serial</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {equipmentQuery.data?.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-semibold text-ink">{item.name}</td>
                  <td className="px-4 py-3 capitalize text-slate-600">{item.type}</td>
                  <td className="px-4 py-3 text-slate-600">{item.serial_number}</td>
                  <td className="px-4 py-3 text-slate-600">{item.location ?? "Unassigned"}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge status={item.status} />
                      <select
                        className="form-input w-36"
                        value={item.status}
                        onChange={(event) =>
                          statusMutation.mutate({
                            id: item.id,
                            status: event.target.value as EquipmentStatus
                          })
                        }
                      >
                        {statuses.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <button
                        className="btn-secondary"
                        onClick={() => {
                          setEditing(item);
                          setIsFormOpen(true);
                        }}
                      >
                        Edit
                      </button>
                      {isRole("equipment_manager", "admin") && (
                        <button
                          className="btn-danger"
                          onClick={() => {
                            if (window.confirm(`Delete ${item.name}?`)) {
                              deleteMutation.mutate(item.id);
                            }
                          }}
                        >
                          Delete
                        </button>
                      )}
                    </div>
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

function EquipmentForm({
  defaults,
  isSubmitting,
  onSubmit,
  onCancel
}: {
  defaults: EquipmentPayload;
  isSubmitting: boolean;
  onSubmit: (payload: EquipmentPayload) => void;
  onCancel: () => void;
}) {
  const { register, handleSubmit } = useForm<EquipmentPayload>({ values: defaults });

  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <label className="text-sm font-semibold text-slate-700">
          Name
          <input className="form-input mt-1" {...register("name", { required: true })} />
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Type
          <input className="form-input mt-1" {...register("type", { required: true })} />
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Serial number
          <input className="form-input mt-1" {...register("serial_number", { required: true })} />
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Location
          <input className="form-input mt-1" {...register("location")} />
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Max rental days
          <input
            className="form-input mt-1"
            type="number"
            min={1}
            {...register("max_rental_days", { valueAsNumber: true, min: 1 })}
          />
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Image URL
          <input className="form-input mt-1" {...register("image_url")} />
        </label>
        <label className="text-sm font-semibold text-slate-700 md:col-span-2">
          Technical spec
          <textarea className="form-input mt-1 min-h-24" {...register("technical_spec")} />
        </label>
        <div className="flex gap-2 md:col-span-2">
          <button className="btn-primary" disabled={isSubmitting}>
            Save equipment
          </button>
          <button className="btn-secondary" type="button" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}
