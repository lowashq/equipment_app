import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { createFaultReport } from "../../api/faultReports";

interface FaultReportFormProps {
  equipmentId: string;
}

export default function FaultReportForm({ equipmentId }: FaultReportFormProps) {
  const { register, handleSubmit, reset } = useForm<{ description: string }>();
  const [message, setMessage] = useState("");

  const mutation = useMutation({
    mutationFn: (description: string) => createFaultReport({ equipment_id: equipmentId, description }),
    onSuccess: () => {
      reset();
      setMessage("Fault report submitted.");
    }
  });

  return (
    <form
      className="space-y-3"
      onSubmit={handleSubmit((values) => mutation.mutate(values.description))}
    >
      <textarea
        className="form-input min-h-28"
        placeholder="Describe the issue"
        {...register("description", { required: true })}
      />
      <button className="btn-primary" disabled={mutation.isPending}>
        Submit report
      </button>
      {message && <p className="text-sm font-semibold text-green-700">{message}</p>}
    </form>
  );
}
